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
        # 将 waiter 实例的 get 方法的返回值作为此函数的返回值
        return waiter.get()

    def set_result(self, data):
        # 调用 writer 的 switch 方法
        self.callback(data)


class Waiter:
    def __init__(self):
        # main_gr 也是协程，是所有爬虫协程的父协程
        self.main_gr = main_gr
        #self.greenlet = None

    def switch(self, value):
        # 切换协程，切换到当时保存的协程
        self.gr.switch(value)

    def get(self):
        # 将当前协程赋值给 greenlet 属性
        # 当前协程就是 Crawler 实例的 fetch 方法
        self.gr = greenlet.getcurrent()
        return self.main_gr.switch()


class Crawler:
    def __init__(self, url):
        self._url = url
        self.url = urlparse(url)
        self.response = b''

    def fetch(self):
        global stopped
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
        # 写事件的回调函数，套接字的写事件就绪时自动运行此函数
        def writable():
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
        # 读事件的回调函数，套接字的读事件就绪时自动运行此函数
        def readable():
            h.set_result(sock.recv(4096))
        # 注册监听套接字的读事件，顺便注册回调函数
        selector.register(sock.fileno(), EVENT_READ, readable)
        while True:
            data = h.wait()
            if data:
                self.response += data
            else:
                # 数据接收完，注销对客户端的监听
                selector.unregister(sock.fileno())
                # 从链接列表中移除此 URL
                urls.remove(self._url)
                if not urls:
                    stopped = True
                # 将图片数据存入本地文件
                with open('pic' + self.url.path, 'wb') as file:
                    file.write(self.response.split(b'\r\n\r\n')[1]) 
                print('URL: {} 下载完成'.format(self.url.path))
                break


def crawler():
    for url in urls:
        # 创建 Crawler 类的实例
        crawler = Crawler(url)
        # 将该实例的 fetch 方法变成协程对象，此协程为 main_gr 的子协程
        gr = greenlet(crawler.fetch)
        gr.switch()


# 将 crawler 函数作为参数创建协程，该协程为主协程或父协程
# 在此协程内部会创建其子协程
main_gr = greenlet(crawler)


# 事件循环函数
def loop():
    while not stopped:
        events = selector.select()
        for event_key, _ in events:
            callback = event_key.data
            callback()


def main():
    start = time.time()
    os.system('mkdir -p pic')
    # 切换到父协程 main_gr 中执行
    main_gr.switch()
    # 开始事件循环
    loop()
    # 打印运行时间
    print("总共耗时: {:.3f}s".format(time.time() - start))


if __name__ == '__main__':
    main()