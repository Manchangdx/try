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
        'https://dn-simplecloud.shiyanlou.com/1517282865454.png'
]

class Watcher:
    def __init__(self, loop, fd):
        self.loop = loop
        self.fd = fd
        # 使用pyuv的Poll方法
        # Poll实例可以监控一个文件描述符的读写事件
        self.watcher = pyuv.Poll(loop.loop, fd)

    def start(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def register(self, events):
        # 注册事件，在事件发生之后执行回调方法run
        self.watcher.start(events, self.run)

    def run(self, watcher, revents, error):
        # 执行回调方法
        self.callback(*self.args, **self.kwargs)

    def stop(self):
        # 停止执行
        self.watcher.stop()


class Loop:
    # 初始化定义一个空队列和一个空列表
    def __init__(self):
        # 空队列用于存储爬虫函数生成的协程的 switch 方法及其参数的元组
        # 协程的 switch 方法首次被调用时，等效于预激协程
        # 程序运行之初向该队列添加元素，添加完毕后，该队列只使用一次
        # 用于预激爬虫实例的 fetch 协程
        self.fetch_funcs_and_args_list = deque()
        # default_loop 用于获取系统中最优的事件库
        self.loop = pyuv.Loop.default_loop()

    # 首次调用爬虫协程的 switch 方法启动协程
    def _run_fetch_switch_first(self):
        while self.fetch_funcs_and_args_list:
            fetch_switch, args, kw = self.fetch_funcs_and_args_list.popleft()
            fetch_switch(*args, **kw)

    def add_fetch_func(self, fun, *args, **kwargs):
        self.fetch_funcs_and_args_list.append((fun, args, kwargs))

    def io(self, watcher, events):
        # 注册io事件，只需要注册事件，pyuv会处理注册的事件集合
        watcher.register(events)
        return watcher

    # 事件循环的主方法，该方法被 Hub 的单例调用
    def run(self):
        # 首次运行全部爬虫协程
        self._run_fetch_switch_first()
        while not stopped:
            # pyuv进行事件循环处理
            self.loop.run()


class Hub(greenlet):
    def __init__(self):
        self.loop = Loop()
        greenlet.__init__(self)

    def wait(self, watcher, events):
        # 注册事件，在wait方法中注册事件
        self.loop.io(watcher, events)
        waiter = Waiter()
        watcher.start(waiter.switch)
        return waiter.get()

    def run(self):
        # 开始事件循环
        self.loop.run()


hub = Hub()


class Waiter:

    def __init__(self):
        self.greenlet = None

    def switch(self):
        self.greenlet.switch()

    def get(self):
        self.greenlet = greenlet.getcurrent()
        hub.switch()


class Client:
    def __init__(self):
        self.sock = socket.socket()
        # 设置为非阻塞
        self.sock.setblocking(False)
        # 初始化watcher，使用pyuv的Poll方法监控socket的文件描述符
        self.watcher = Watcher(hub.loop, self.sock.fileno())

    def connect(self, address):
        addrinfo = pyuv.dns.getaddrinfo(hub.loop.loop, address)
        if not addrinfo:
            return
        ip = addrinfo[-1].sockaddr[0]
        try:
            self.sock.connect((ip, 80))
        except BlockingIOError:
            pass

    def write(self, data):
        # 注册写事件，并且切换到hub协程执行
        # 创建waiter实例，保存当前协程，将switch方法赋值给watcher的callback
        # 执行事件循环，在事件发生之后，回调执行watcher的run方法，run方法执行watcher的callback方法
        # 执行waiter的switch方法，切换到当前协程开始继续执行
        hub.wait(self.watcher, pyuv.UV_WRITABLE)
        self.sock.send(data.encode('ascii'))

    def read(self):
        # 注册读事件，并且切换到hub，读事件发生之后再切换回来执行
        hub.wait(self.watcher, pyuv.UV_READABLE)
        return self.sock.recv(1024)

    def read_all(self):
        response = b''
        while True:
            chunk = self.read()
            if not chunk:
                break
            response += chunk
        return response

    def close(self):
        # 关闭socket
        self.sock.close()
        # 关闭事件监听
        self.watcher.stop()


class Crawler:
    def __init__(self, url):
        self._url = url
        self.url = urlparse(url)
        self.response = b''

    def fetch(self):
        global stopped
        client = Client()
        # 建立连接，异步执行被隐藏起来
        client.connect(self.url.netloc)
        value = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n' \
                .format(self.url.path, self.url.netloc)
        # 向服务端发送数据
        client.write(value)
        # 读取服务端数据
        response = client.read_all()
        # 关闭客户端
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


if __name__ == '__main__':
    start = time.time()
    os.system('mkdir -p pic')
    for url in urls:
        crawler = Crawler(url)
        spawn(crawler.fetch)
    hub.switch()
    print('程序运行耗时：{:.3f}s'.format(time.time() - start))