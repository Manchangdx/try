import socket
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ 

selector = DefaultSelector()
stopped = False

urls = {'/', '/1', '/2', '/3', '/4', '/5', '/6', '/7', '/8', '/9'}

HOST = 'localhost'
PORT = 8000

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

    def __iter__(self):
        yield self
        return self.result

class AsyncSocket:

    def __init__(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)

    def connect(self, address):
        f = Future()
        try:
            self.sock.connect(address)
        except BlockingIOError:
            pass

        def on_connected():
            f.set_result(None)

        selector.register(self.sock.fileno(), EVENT_WRITE, on_connected)
        yield from f
        selector.unregister(self.sock.fileno())

    def send(self, data):
        self.sock.send(data)

    def read(self):
        f = Future()

        def on_readable():
            f.set_result(self.sock.recv(4096))

        selector.register(self.sock.fileno(), EVENT_READ, on_readable)
        chunk = yield from f
        selector.unregister(self.sock.fileno())
        return chunk

class Crawler:
    def __init__(self, url):
        self.url = url
        self.response = b''

    def fetch(self):
        global stopped
        sock = AsyncSocket()
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
