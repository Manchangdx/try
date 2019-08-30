import time
import os
import socket
import pyuv
from collections import deque
from urllib.parse import urlparse
from greenlet import greenlet

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


class Watcher:
    def __init__(self, loop, fd):
        # 创建一个 Poll 类的实例，须提供事件循环对象和套接字的文件描述符作为参数
        # 该实例有一个 start 方法，提供事件常数和回调函数即可调用此方法
        # 执行此方法后，loop 对象就会注册监听此套接字的相关事件
        self.poll = pyuv.Poll(loop.loop, fd)
        # 回调函数，即当前协程的 switch 方法
        # 上面已经介绍，调用 Poll 实例的 start 方法时会将这个回调函数作为参数
        self.callback = greenlet.getcurrent().switch


class Loop:
    # 初始化定义一个空队列和一个空列表
    def __init__(self):
        # 空队列用于存储爬虫函数生成的协程的 switch 方法及其参数的元组
        # 协程的 switch 方法首次被调用时，等效于预激协程
        # 程序运行之初向该队列添加元素，添加完毕后，该队列只使用一次
        # 用于预激爬虫实例的 fetch 协程
        self.fetch_funcs_and_args_list = deque()
        # 创建 loop 事件循环对象，pyuv 自动选择系统中性能最好的 I/O 模型
        self.loop = pyuv.Loop.default_loop()

    # 首次调用爬虫协程的 switch 方法启动协程
    def _run_fetch_switch_first(self):
        while self.fetch_funcs_and_args_list:
            fetch_switch, args, kw = self.fetch_funcs_and_args_list.popleft()
            fetch_switch(*args, **kw)

    def add_fetch_func(self, fun, *args, **kwargs):
        self.fetch_funcs_and_args_list.append((fun, args, kwargs))

    # 事件循环的主方法，该方法被 Hub 的单例调用
    def run(self):
        # 首次运行全部爬虫协程
        self._run_fetch_switch_first()
        # 全部爬虫协程创建各自的客户端套接字并向服务器发送连接请求后，向下执行事件循环
        while not stopped:
            # 调用 loop 对象的 run 方法启动事件循环
            self.loop.run()


class Hub(greenlet):
    def __init__(self):
        self.loop = Loop()
        super().__init__(self)

    # 该类的实例调用 switch 方法启动协程之后将执行 run 方法
    def run(self):
        self.loop.run()


hub = Hub()


class Client:
    def __init__(self):
        self.sock = socket.socket()     # 创建客户端套接字
        self.sock.setblocking(False)    # 将客户端套接字设置为非阻塞
        # 初始化 Watcher 类需要提供 loop 事件循环对象和套接字的文件描述符作为参数
        # Watcher 类的实例有 poll 属性，该属性值为 pyuv.Poll 的实例
        # 该实例用于注册监听套接字的相关事件
        self.watcher = Watcher(hub.loop, self.sock.fileno())

    # 该方法用于向服务器发送连接请求，然后注册监听套接字的写事件
    def connect(self, address):
        # 以下四行是为了获取图片所在的服务器的 IP 地址，用以向服务器发送连接请求
        # 其实可以注释掉这四行，直接使用参数 address 域名亦可
        addrinfo = pyuv.dns.getaddrinfo(hub.loop.loop, address)
        if not addrinfo:
            return
        ip = addrinfo[-1].sockaddr[0]
        # 向图片所在服务器发送连接请求
        try:
            self.sock.connect((ip, 80))
        except BlockingIOError:
            pass
        # Poll 实例调用 start 方法注册监听套接字的写事件，并提供回调函数
        self.watcher.poll.start(pyuv.UV_WRITABLE, self.watcher.callback)
        # 切换到 hub 主协程中执行
        hub.switch()

    # 向服务器发送数据，然后注册监听套接字的读事件
    def write(self, value):
        self.sock.send(value.encode())
        self.watcher.poll.start(pyuv.UV_READABLE, self.watcher.callback)
        hub.switch() 

    # 读取服务器返回的数据，每读取一次就切换回 hub 协程
    def read_all(self):
        response = b''
        while True:
            chunk = self.sock.recv(1024)
            if not chunk:
                break
            response += chunk
            hub.switch() 
        # 读取完毕，返回全部数据
        return response

    def close(self):
        self.sock.close()           # 关闭套接字
        self.watcher.poll.stop()    # 注销事件监听


class Crawler:
    def __init__(self, url):
        self._url = url
        self.url = urlparse(url)

    def fetch(self):
        global stopped
        # 创建 Client 实例，该实例用于处理客户端套接字相关操作
        client = Client()
        # 调用此方法向服务器发送连接请求，然后切换到 hub 协程
        client.connect(self.url.netloc)
        # 连接成功后，可写事件就绪，调用回调函数切回该爬虫协程继续执行
        value = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n' \
                .format(self.url.path, self.url.netloc)
        # 调用此方法向服务器发送数据，然后切换到 hub 协程
        client.write(value)
        # 服务器返回数据后，可读事件就绪，切回该爬虫协程继续执行
        # real_all 方法中有 while 循环，多次读取数据片段，直到接收完毕全部数据并返回
        # 在此过程中，会在爬虫协程与 hub 协程中切换多次
        response = client.read_all()
        # 关闭套接字，注销对套接字的监听
        client.close()  
        urls.remove(self._url)
        with open('pic' + self.url.path, 'wb') as file:
            file.write(response.split(b'\r\n\r\n')[1]) 
        print("URL: {0} 下载完成".format(self._url))
        if not urls:
            stopped = True


# 此方法用于创建爬虫协程
def spawn(fun, *args, **kw):
    # greenlet 是协程类，该类的实例为协程对象
    # 实例化需要提供两个参数：协程函数和父协程（第二个参数选填）
    # fun 的值为爬虫实例的 fetch 方法，父协程为 hub
    # 在 fetch 方法的协程运行结束之后，自动返回到父协程中继续执行
    g = greenlet(fun, hub)
    # 将协程的 switch 方法及其参数组成元组
    # 加入到 loop 的 fetch_funcs_and_args_list 队列中
    hub.loop.add_fetch_func(g.switch, *args, **kw)


def main():
    start = time.time()
    os.system('mkdir -p pic')
    for url in urls:
        crawler = Crawler(url)
        spawn(crawler.fetch)
    hub.switch()
    print('程序运行耗时：{:.3f}s'.format(time.time() - start))


if __name__ == '__main__':
    main()