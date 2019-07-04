import time
import socket
from urllib.parse import urlparse
# selectors 是对 select 的封装，它会根据不同的操作系统自动选择适合的系统调用
# DefaultSelector 类的实例是系统调用，类似 select、poll、epoll 
# EVENT_READ 和 EVENT_WRITE 是事件常数，值为 1 和 2
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

selector = DefaultSelector()
# 需要爬取图片的地址列表
urls = ['https://dn-simplecloud.shiyanlou.com/ncn1.jpg',
        'https://dn-simplecloud.shiyanlou.com/ncn110.jpg',
        'https://dn-simplecloud.shiyanlou.com/ncn109.jpg',
        'https://dn-simplecloud.shiyanlou.com/1548126810319.png',
        'https://dn-simplecloud.shiyanlou.com/1517282865454.png'
]


# 该类用来模拟发送「协助事件循环停止运行」的信号
class Signal:
    def __init__(self):
        self.stop = False


signal = Signal()


# 定义一个爬虫类
class Crawler:
    def __init__(self, url):
        # urlparse 方法用来处理 URL ，其返回值便于获得域名和路径
        self.url = urlparse(url)
        self._url = url
        self.response = b''

    def fetch(self):
        # 创建 socket 实例
        self.sock = socket.socket()
        # 将客户端套接字设置为非阻塞模式
        self.sock.setblocking(False)
        try:
            # 连接需要时间，非阻塞模式下这里会报出 BlockingIOError 异常
            self.sock.connect((self.url.netloc, 80))
        except BlockingIOError:
            pass
        # 向 selector 这个系统调用中注册套接字的可写事件
        # 参数为套接字的文件描述符、事件常数、回调函数
        # 当连接服务器成功后，可写事件会立即就绪，然后自动执行对应的回调函数
        # 注意回调函数的执行不是由操作系统决定的，而是由 selector 内部控制
        selector.register(self.sock.fileno(), EVENT_WRITE, self.writable)

    # 套接字可写事件就绪后，自动运行此回调函数
    # 所有回调函数的参数都是固定的：SelectorKey 实例，事件常数（选填）
    def writable(self, key):
        # 可写事件就绪后，这个事件就不需要再监听了，注销此事件
        # 不注销的话，selector 就一直提醒事件已就绪
        # SelectorKey 实例的 fd 属性值为对应的套接字的文件描述符
        selector.unregister(key.fd)
        print('连接成功', key.fd)
        # 向服务器发送数据，这是网页请求的固定格式
        data = 'GET {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format(
            self.url.path, self.url.netloc)
        self.sock.send(data.encode())
        print('发送数据成功', key.fd)
        # 接收数据后，监视套接字的可读事件并设置回调函数
        # 在套接字的可读事件就绪后，自动运行回调函数
        selector.register(self.sock.fileno(), EVENT_READ, self.readable)

    # 套接字可读事件就绪后，自动运行此回调函数
    # 可读事件就绪，并不代表内核空间已经接收完全部数据
    def readable(self, key):
        print('接收数据', key.fd)
        # 接收服务器返回的数据，注意这步是从内核空间复制数据到用户空间
        # 每次最多接收 100K 数据，如果数据量比较大，该回调函数会运行多次
        # 只要内存空间里有数据，相关套接字的可读事件就会就绪
        # 所以每次 recv 方法收到的数据很可能不足 100k 
        d = self.sock.recv(102400)
        if d:
            self.response += d
        else:
            # 可读事件一直被监听，直到接收数据为空，接收完毕
            # 就不需要再监听此事件了，注销它
            selector.unregister(key.fd)
            print('接收数据成功', key.fd)
            # 注意第一个参数 self.url.path 的第一个字符为斜杠，须去掉
            # 接收到的数据为二进制，其中第一部分为报头，第二部分为图片数据
            # 两部分之间使用 \r\n\r\n 隔开，选择第二部分存入文件
            with open(self.url.path[1:], 'wb') as f:
                f.write(self.response.split(b'\r\n\r\n')[1])
            print('保存文件成功')
            self.sock.close()
            # 接收数据完毕，从需要爬取的地址列表中删除此地址
            urls.remove(self._url)
            # 如果地址列表为空
            # 修改 signal 的属性值，停止 loop 函数中的 while 循环 
            if not urls:
                signal.stop = True


def loop():
    # 事件循环，不停地查询被监听的事件是否就绪
    while not signal.stop:
        print('-------------------')
        # selector.select 方法为非阻塞运行
        # 只是轮询被监听事件，立即返回就绪事件列表
        # 该方法的功能类似于 select().select 方法，具体用法不同
        events = selector.select()
        # 事件列表中每个事件是一个元组，元组里有俩元素
        # 分别是 SelectorKey 对象和事件常数
        print(events)
        for event_key, event_mask in events:
            # SelectorKey 对象的 data 属性值就是回调函数
            callback = event_key.data
            # 运行回调函数
            callback(event_key)


def main():
    start = time.time()
    for url in urls:
        # 创建爬虫实例
        crawler = Crawler(url)
        # 执行此方法后，将创建一个套接字，套接字向服务器发送连接请求后
        # 将套接字的可写事件注册到 selector 中
        crawler.fetch()
    loop()  # 运行事件循环 + 回调函数
    print('耗时：{:.2f}s'.format(time.time() - start))


if __name__ == '__main__':
    main()
