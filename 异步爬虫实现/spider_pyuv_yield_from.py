# File Name: spider_pyuv_yield_from.py

import time
import os
import pyuv
from urllib.parse import urlparse

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
        self._callbacks = []

    def set_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn()

    # 实现 __iter__ 方法，Future 类的实例为可迭代对象
    def __iter__(self):
        # 该语句起到暂停协程的作用，并返回实例本身
        yield self
        # 该语句定义的返回值会赋给 yield from 语句等号前面的变量
        return self.result


class Client:
    def __init__(self, loop):
        # 参数 loop 会自动选用平台上最优的 I/O 模型创建 TCP 客户端
        self.client = pyuv.TCP(loop)
        self.result = b''

    # 该方法用于连接服务器
    def connect(self, address):
        f = Future()
        # 回调方法，在连接到服务端之后调用
        # 连接服务器成功后，客户端套接字的可写事件就行，调用此回调函数
        def writable(handler, error):
            f.set_result(None)
        # 向服务器发送连接请求，顺便注册回调函数，pyuv 自动监听套接字的可写事件
        self.client.connect(address, writable)
        # Future类实现了__iter__方法，其实例可以写在 yield from 语句之后
        yield from f

    # 发送数据给服务端
    def write(self, data):
        self.client.write(data.encode())

    def read(self):
        f = Future()
        # 该函数为回调函数，客户端的可读事件就绪时，读取服务端数据
        def readable(handler, data, error):
            if data:
                self.result += data
            else:
                f.set_result(self.result)
        # 注册监听 client 的可读事件，将 readable 作为回调函数 
        self.client.start_read(readable)
        response = yield from f
        return response

    def close(self):
        self.client.close()


class Crawler:
    def __init__(self, url, loop):
        self._url = url
        self.url = urlparse(url)
        self.response = b''
        self.loop = loop

    def fetch(self):
        # 使用 DNS 解析域名，获取图片服务器相关信息
        addrinfo = pyuv.dns.getaddrinfo(self.loop, self.url.netloc)
        if not addrinfo:
            return
        ip = addrinfo[-1].sockaddr[0]
        # 将事件循环 self.loop 作为参数创建 Client 类的实例
        client = Client(self.loop)
        # connect方法是协程，使用yield from可以将数据直接传输给connect方法
        # 在子协程执行完之后，才会继续向下执行
        yield from client.connect((ip, 80))
        data = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n' \
                .format(self.url.path, self.url.netloc)
        client.write(data)
        self.response = yield from client.read()
        # 关闭客户端套接字，pyuv 自动注销对其监听
        client.close()
        with open('pic' + self.url.path, 'wb') as file:
            file.write(self.response.split(b'\r\n\r\n')[1])
        print(self.url.path[1:], '已保存')


class Task:
    def __init__(self, coro):
        self.coro = coro
        self.step()

    def step(self):
        try:
            new_future = self.coro.send(None)
        except StopIteration:
            return
        new_future.set_done_callback(self.step)


def main():
    start = time.time()
    os.system('mkdir -p pic')
    # 创建 loop 事件循环对象，pyuv 自动选择系统中性能最好的 I/O 模型
    loop = pyuv.Loop.default_loop()
    for url in urls:
        crawler = Crawler(url, loop)
        Task(crawler.fetch())
    loop.run()
    print("程序运行耗时: {:.3f}s".format(time.time() - start))


if __name__ == '__main__':
    main()