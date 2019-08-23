import socket
import os
import time
from greenlet import greenlet
from urllib.parse import urlparse
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ

selector = DefaultSelector()
stopped = False

urls = ['https://dn-simplecloud.shiyanlou.com/ncn1.jpg',
        'https://dn-simplecloud.shiyanlou.com/ncn110.jpg',
        'https://dn-simplecloud.shiyanlou.com/ncn109.jpg',
        'https://dn-simplecloud.shiyanlou.com/1548126810319.png',
        'https://dn-simplecloud.shiyanlou.com/1517282865454.png',
        'https://dn-simplecloud.shiyanlou.com/1543913883545.png',
        'https://dn-simplecloud.shiyanlou.com/1502778396172.png',
        'https://dn-simplecloud.shiyanlou.com/1540965522764.png',
        'https://dn-simplecloud.shiyanlou.com/1546500900109.png',
        'https://dn-simplecloud.shiyanlou.com/1547620906601.png'
]

# Hub 类，控制协程的切换
class Hub():
    def wait(self):
        # 创建 Waiter 类的实例
        waiter = Waiter()
        # 设置回调方法为 waiter 的 switch 方法
        self.callback = waiter.switch
        return waiter.get()

    def set_result(self, data):
        # 调用 writer 的 switch 方法
        self.callback(data)


class Waiter:
    def __init__(self):
        # main 也是协程，是所有爬虫协程的父协程
        self.main = main
        self.greenlet = None

    def switch(self, value):
        # 切换协程，切换到当时保存的协程
        self.greenlet.switch(value)

    def get(self):
        # 将当前协程赋值给 greenlet 属性
        # 当前协程就是 Crawler 实例的 fetch 方法
        self.greenlet = greenlet.getcurrent()
        try:
            # 切换执行主协程
            return self.main.switch()
        finally:
            self.greenlet = None


class Crawler:
    def __init__(self, url):
        self._url = url
        self.url = urlparse(url)
        self.response = b''

    def fetch(self):
        self.time = time.time()
        # 创建客户端套接字
        sock = socket.socket()
        # 将套接字设置为非阻塞
        sock.setblocking(False)
        # 向服务器发送连接请求，参数为域名和端口号的元组
        try:
            sock.connect((self.url.netloc, 80))
        except BlockingIOError:
            pass
        # 创建 Hub 类的实例
        h = Hub()
        # 可写事件的回调函数，套接字的可写事件就绪时自动运行此函数
        def writable():
            # 可写事件发生之后，调用回调方法 writable
            # 再 Hub 的 set_result 方法中开始调用 callback 方法
            # callback 方法是 waiter 的 switch 方法，所以调用的是 waiter.switch 方法
            # switch 方法中有调用的是 greenlet 的 switch 方法
            # greenlet 是保存的当前的协程，所以又切换回来继续执行
            # 是用 wait 方法切换出去的，这时候再从 wait 方法继续执行
            h.set_result(None)
        # 注册监听套接字的写事件，顺便注册回调函数
        selector.register(sock.fileno(), EVENT_WRITE, writable)
        h.wait()
        # 切换回来注销套接字的事件监听
        selector.unregister(sock.fileno())
        data = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n' \
                .format(self.url.path, self.url.netloc)
        # 向服务器发送请求
        sock.send(data.encode())
        global stopped
        while True:
            def readable():
                # 在可读事件发生之后
                # socket 接收服务端发生的数据
                # 将数据值通过 switch 方法传给当前协程
                h.set_result(sock.recv(4096))
            # 注册监听客户端套接字的读事件
            selector.register(sock.fileno(), EVENT_READ, readable)
            # 保存当前协程，并切换到 main 协程上执行
            # 接收到的值会通过 switch 方法传递过来，赋值给 chunk
            chunk = h.wait()
            # 切换回来注销事件
            selector.unregister(sock.fileno())
            # 在协程执行结束之后，会返回到父协程的方法中继续执行
            if chunk:
                self.response += chunk
            else:
                # 数据接收完
                urls.remove(self._url)
                if not urls:
                    stopped = True
                # 将图片数据存入本地文件
                with open('pic' + self.url.path, 'wb') as file:
                    file.write(self.response.split(b'\r\n\r\n')[1]) 
                print("URL: {0}, 耗时: {1:.3f}s".format(self._url, time.time() - self.time))
                break


# 爬虫
def crawler():
    for url in urls:
        # 创建爬虫对象
        c = Crawler(url)
        # 生成 greenlet 协程
        g = greenlet(c.fetch)
        # 切换执行
        x = g.switch()
        print(x)


# 爬虫协程都是在 main 协程中创建，所以是所有爬虫协程的父协程
# 在爬虫协程执行完之后，会切换回父协程 main，避免出现资源未关闭的情况
main = greenlet(crawler)


def loop():
    while not stopped:
        events = selector.select()
        for event_key, _ in events:
            callback = event_key.data
            callback()


def ain():
    start = time.time()
    os.system('mkdir -p pic')
    # 切换到主协程中执行
    main.switch()
    # 开始事件循环
    loop()
    # 打印运行时间
    print("总共耗时: {:.3f}s".format(time.time() - start))


if __name__ == '__main__':
    ain()