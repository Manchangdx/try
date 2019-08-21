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

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)


class Crawler:
    # 初始化，参数 loop 是 pyuv 生成的事件循环对象
    def __init__(self, url, loop):
        self._url = url
        self.response = b''
        self.loop = loop

    def fetch(self):
        self.url = urlparse(self._url)
        # 使用 DNS 解析域名，获取图片服务器相关信息
        addrinfo = pyuv.dns.getaddrinfo(self.loop, self.url.netloc)
        if not addrinfo:
            print('图片链接不正确')
            return
        ip = addrinfo[-1].sockaddr[0]
        # 参数 self.loop 会自动选用平台上最优的 I/O 模型创建 TCP 客户端
        client = pyuv.TCP(self.loop)
        f = Future()
        # 该方法为回调函数，服务器连接成功后套接字可写事件就绪，自动运行此函数
        # pyuv 内部会调用此方法，参数 handler 的值就是 client 
        # 由于协程可以保存上下文环境，可以继续使用 client 实例
        def writable(handler, error):
            f.set_result(None)
        # 向服务器发送连接请求，self.writable 方法作为回调函数
        # 同时 loop 自动注册监听 client 的可写事件
        client.connect((ip, 80), writable)
        # 暂停执行，返回上一级函数 Task.step 继续执行
        yield f
        data = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n' \
                .format(self.url.path, self.url.netloc)
        # 向服务端发送数据，这里无需提供回调函数
        client.write(data.encode())
        f = Future()
        # 客户端套接字可读就绪时，自动运行此回调函数
        # 此函数会运行多次，直到接收完毕全部数据
        def readable(handler, data, error):
            if data:
                self.response += data
            else:
                # 接收完毕全部数据，调用此方法继续运行协程
                f.set_result(None)
        # 注册监听 client 的可读事件，将 readable 作为回调函数 
        client.start_read(readable)
        # 将 Future 类的新实例返回给 new_future 变量
        yield f
        client.close()
        # 将读取的图片数据存入文件
        with open('pic' + self.url.path, 'wb') as file:
            file.write(self.response.split(b'\r\n\r\n')[1]) 
        print(self.url.path[1:], '已保存')


class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        self.step(f)

    def step(self, future):
        try:
            new_future = self.coro.send(future.result)
        except StopIteration:
            return
        new_future.add_done_callback(self.step)


def main():
    start = time.time()
    os.system('mkdir -p pic')
    loop = pyuv.Loop.default_loop()
    for url in urls:
        crawler = Crawler(url, loop)
        Task(crawler.fetch())
    loop.run()
    print("程序运行总耗时: {:.3f}s".format(time.time() - start))


if __name__ == '__main__':
    main()
