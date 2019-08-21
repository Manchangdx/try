# File Name: spider_yield_from.py

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
        self.value = None
        self._step_func = []

    def add_step_func(self, func):
        self._step_func.append(func)

    def set_value(self, value):
        self.value = value
        for func in self._step_func:
            func(self)

    # 实现 __iter__ 方法，Future 类的实例为可迭代对象
    def __iter__(self):
        # 该语句起到暂停协程的作用，并返回实例本身
        yield self          
        # 该语句定义的返回值会赋给 yield from 语句等号前面的变量
        return self.value


# AsyncSocket 类封装套接字，该类的实例拥有套接字的各种接口
# 因为主要方法都是协程函数，所以该类以 Async 作为标识
class AsyncSocket:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)

    # 该方法用于向服务器发送连接请求并注册监听套接字的可写事件
    def connect(self, address):
        f = Future()
        try:
            self.sock.connect(address)
        except BlockingIOError:
            pass
        # 这是回调函数，服务器与客户端连接成功后自动执行
        def writable():
            f.set_value(None)
        # 注册监听客户端套接字的可写事件
        selector.register(self.sock.fileno(), EVENT_WRITE, writable)
        # 可迭代对象 f 为 Future 类的实例
        # 执行此行代码，程序会运行到 f.__iter__ 方法的 yield 语句处暂停
        # 将 yield 后面的对象返回给调用者并赋值给 step 方法内的 new_future 变量
        yield from f
        selector.unregister(self.sock.fileno())

    # 向服务器发送获取图片的请求
    def send(self, data):
        self.sock.send(data)

    # 该方法会多次执行，以获取服务器返回的数据片段
    def read(self):
        f = Future()
        # 这是回调函数，收到服务器传回的数据时自动运行
        def readable():
            f.set_value(self.sock.recv(4096))
        # 注册监听客户端套接字的可读事件
        selector.register(self.sock.fileno(), EVENT_READ, readable)
        # f.__iter__ 方法的返回值会赋值给 value 变量
        value = yield from f
        selector.unregister(self.sock.fileno())
        return value

    # 关闭客户端套接字
    def close(self):
        self.sock.close()


# 爬虫类，该类的实例的 fetch 方法用于处理数据
# 期间会调用 AsyncSocket 类的实例来完成数据获取的工作
class Crawler:
    def __init__(self, url):
        self._url = url
        self.url = urlparse(url)
        self.response = b''

    def fetch(self):
        # 将此变量设为全局变量，以便在函数内部修改
        global stopped
        self.time = time.time()
        # AsyncSocket 类的实例对象负责完成数据获取的工作
        sock = AsyncSocket()
        # 向服务器发送连接请求，协程会暂停到嵌套协程中的某个 yield 处
        yield from sock.connect((self.url.netloc, 80))
        data = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n \
                '.format(self.url.path, self.url.netloc)
        sock.send(data.encode())
        # 不断循环以读取服务器返回的数据片段，直到数据返回空
        while True:
            # sock.read 方法会调用 Future 类的实例的 __iter__ 方法
            # __iter__ 方法的 return 值即服务器返回的数据片段会赋给 value 变量
            value = yield from sock.read()
            if value:
                self.response += value
            else:
                sock.close()
                with open('pic' + self.url.path, 'wb') as file:
                    file.write(self.response.split(b'\r\n\r\n')[1])
                print("URL: {0}, 耗时: {1:.3f}s".format(
                        self._url, time.time() - self.time))
                urls.remove(self._url)
                if not urls:
                    stopped = True
                break


class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        self.step(f)

    def step(self, future):
        try:
            new_futrue = self.coro.send(future.value)
        except StopIteration:
            return
        new_futrue.add_step_func(self.step)


def loop():
    while not stopped:
        events = selector.select()
        for event_key, _ in events:
            callback = event_key.data
            callback()


def main():
    os.system('mkdir -p pic')
    start = time.time()
    for url in urls:
        crawler = Crawler(url)
        Task(crawler.fetch())
    loop()
    print("总共耗时: {:.3f}s".format(time.time() - start))


if __name__ == '__main__':
    main()
