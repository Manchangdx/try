import socket
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ 

selector = DefaultSelector()
stopped = False

urls = {'/', '/1', '/2', '/3', '/4', '/5', '/6', '/7', '/8', '/9'}

HOST = 'localhost'
PORT = 1234

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

    # 实现__iter__方法，Future类为生成器类
    def __iter__(self):
        yield self
        return self.result


class AsyncSocket:

    # 初始化
    def __init__(self):
        self.sock = socket.socket()
        # 设置非阻塞
        self.sock.setblocking(False)

    # 方法中有yield from关键字，说明connect是协程函数
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


class Crawler:
    def __init__(self, url):
        self.url = url
        self.response = b''

    def fetch(self):
        global stopped
        # 异步socket实例
        sock = AsyncSocket()
        # connect是协程，yield from调用子协程
        yield from sock.connect((HOST, PORT))
        get = 'GET {0} HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n'.format(self.url)
        sock.send(get.encode('ascii'))
        self.response = yield from sock.read()
        urls.remove(self.url)
        if not urls:
            stopped = True


class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        self.step(f)

    def step(self, future):
        try:
            next_futrue = self.coro.send(future.result)
        except StopIteration:
            return
        next_futrue.add_done_callback(self.step)


def loop():
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()

if __name__ == '__main__':
    import time
    start = time.time()
    for url in urls:
        crawler = Crawler(url)
        Task(crawler.fetch())

    loop()
    print(time.time() - start)
