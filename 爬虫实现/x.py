# crawler_yield_from.py

import time
import os
import socket
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


class Future:
    def __init__(self):
        self.result = None
        self._add_step_func = []

    def add_done_callback(self, func):
        self._add_step_func.append(func)

    def set_result(self, result):
        self.result = result
        for func in self._add_step_func:
            func(self)

    # 实现 __iter__ 方法，Future 类的实例为 iterable
    def __iter__(self):
        yield self
        return self.result


# AsyncSocket 类封装 socket 类
class AsyncSocket:
    # 初始化
    def __init__(self):
        self.sock = socket.socket()
        # 设置非阻塞
        self.sock.setblocking(False)

    # 方法中有 yield from 关键字，说明 connect 是协程函数
    def connect(self, address):
        f = Future()
        try:
            self.sock.connect(address)
        except BlockingIOError:
            pass

        def on_connected():
            f.set_result(None)

        selector.register(self.sock.fileno(), EVENT_WRITE, on_connected)
        # Future是生成器，yield from调用子协程
        # Future的方法__iter__执行，遇到yield之后暂停执行，返回到connect的上一级调用
        # 调用connect协程的send方式时，yield from并不会立即向下执行，而是继续__iter__方法执行，直到return返回
        # 返回Future实例，Future方法执行结束，yield from才继续向下执行
        yield from f
        selector.unregister(self.sock.fileno())

    def send(self, data):
        self.sock.send(data)

    # 同样是协程函数
    def read(self):
        f = Future()

        def on_readable():
            # 接收客户端的数据，将数据存放到future对象中
            f.set_result(self.sock.recv(4096))

        selector.register(self.sock.fileno(), EVENT_READ, on_readable)
        # 调用子协程
        # __iter__方法最后返回result，yield from会处理接收到返回值，再将值赋值给chunk
        chunk = yield from f
        selector.unregister(self.sock.fileno())
        return chunk

    def close(self):
        self.sock.close()


class Crawler:
    def __init__(self, url):
        self._url = url
        self.url = urlparse(url)
        self.response = b''

    def fetch(self):
        global stopped
        self.time = time.time()
        # 异步socket实例
        sock = AsyncSocket()
        # connect是协程，yield from调用子协程
        yield from sock.connect((self.url.netloc, 80))
        data = 'GET {0} HTTP/1.1\r\nHost: {1}\r\nConnection: close\r\n\r\n \
                '.format(self.url.path, self.url.netloc)
        sock.send(data.encode())
        ###selector.register(sock.fileno(), EVENT_READ, on_readable)
        # 不断的读取数据，直到数据返回空
        while True:
            # 读取数据
            value = yield from sock.read()
            if value:
                self.response += value
            else:
                urls.remove(self._url)
                if not urls:
                    stopped = True
                ###selector.unregister(self.sock.fileno())
                sock.close()
                # 将图片数据存入文件
                with open('pic' + self.url.path, 'wb') as file:
                    file.write(self.response.split(b'\r\n\r\n')[1])
                print("URL: {0}, 耗时: {1:.3f}s".format(self._url, time.time() - self.time))
                break


class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        self.step(f)

    def step(self, future):
        try:
            new_futrue = self.coro.send(future.result)
        except StopIteration:
            return
        new_futrue.add_done_callback(self.step)


def loop():
    while not stopped:
        events = selector.select()
        for event_key, _ in events:
            callback = event_key.data
            callback()

if __name__ == '__main__':
    os.system('mkdir -p pic')
    start = time.time()
    for url in urls:
        crawler = Crawler(url)
        Task(crawler.fetch())
    loop()
    print("总共耗时: {:.3f}s".format(time.time() - start))
