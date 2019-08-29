import time
import os
import socket
from greenlet import greenlet
from collections import deque
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


# 事件监听类
class Watcher:
    # 初始化定义两个属性备用：文件描述符和事件常数
    def __init__(self, fd, event_constant):
        self.fd = fd
        self.event_constant = event_constant
        # 调用此方法注册事件监听
        self._register()

    # 注册事件监听
    def _register(self):
        selector.register(self.fd, self.event_constant)

    # 注销事件监听
    def _unregister(self):
        selector.unregister(self.fd)

    # 套接字的相关事件就绪后，执行此方法注销事件监听并运行回调函数
    # callback 的值实际上是爬虫实例的 fetch 协程的 switch 方法
    def run(self):
        self._unregister()
        self.callback()


# 事件循环类，程序运行过程中，只在 Hub 类实例化时创建一个该类的实例
class Loop:
    # 初始化定义一个空队列和一个空列表
    def __init__(self):
        # 空队列用于存储爬虫函数生成的协程的 switch 方法及其参数的元组
        # 协程的 switch 方法首次被调用时，等效于预激协程
        # 程序运行之初向该队列添加元素，添加完毕后，该队列只使用一次
        # 用于预激爬虫实例的 fetch 协程
        self.fetch_funcs_and_args_list = deque()
        # 空列表用于存储 Watcher 类的实例
        self.watchers = []

    # 首次调用爬虫协程的 switch 方法启动协程
    def _run_fetch_switch_first(self):
        while self.fetch_funcs_and_args_list:
            fetch_switch, args, kw = self.fetch_funcs_and_args_list.popleft()
            fetch_switch(*args, **kw)

    # 该方法在 run 方法内部的 while 循环中被调用
    # 等待事件就绪，就绪后调用事件的相关回调函数
    def _run_watchers(self):
        # selector.select 方法为阻塞运行
        # 轮询被监听事件，如有事件就绪，立即返回就绪事件列表
        ready_events = selector.select()
        # ready_events 是已经准备就绪的事件列表，列表中的元素是元组
        # 元组中包含 SelectorKey 对象和事件常数，事件常数暂时用不到，使用一个下划线接收
        for event_key, _ in ready_events:
            # self.watchers 列表中的元素是 Watcher 类的实例
            # self.watchers[:] 复制一个等值新列表，避免修改原列表时影响 for 循环
            for watcher in self.watchers[:]:
                # 如果 Watcher 类的实例与 event_key 的文件描述符和事件常数相同
                # 则从 self.watchers 列表中移除该实例并运行该实例的 run 方法
                if watcher.fd == event_key.fd and \
                        watcher.event_constant == event_key.events:
                    # 从 watchers 列表中移除 watcher 对象是因为套接字的读事件就绪后
                    # loop.io 方法会向 watchers 列表中重复添加 Watcher 类的实例
                    # 且这些实例的 fd 和 event_constant 属性值相同
                    self.watchers.remove(watcher)
                    # 执行 Wathcer 实例的 run 方法注销事件监听并执行回调
                    watcher.run()

    # 程序运行之初调用此方法将回调方法及其参数的元组加入到队列中
    def add_fetch_func(self, fun, *args, **kw):
        self.fetch_funcs_and_args_list.append((fun, args, kw))

    # 此方法只在爬虫实例的 fetch 方法运行时被调用
    def io(self, fd, event_constant):
        # 创建 Watcher 类的实例，即注册监听套接字的某个事件
        watcher = Watcher(fd, event_constant)
        # 将当前运行的爬虫协程的 switch 方法赋值给 Watcher 实例的 callback 属性
        # watcher.callback 就是套接字事件就绪时被调用的回调函数
        watcher.callback = greenlet.getcurrent().switch
        # 将 watcher 加入到 watchers 列表中备用
        self.watchers.append(watcher)

    # 事件循环的主方法，该方法被 Hub 的单例调用
    def run(self):
        # 首次运行全部爬虫协程
        self._run_fetch_switch_first()
        while not stopped:
            self._run_watchers()


# 继承 greenlet 协程类，需重载 run 方法，该类的实例为协程
class Hub(greenlet):
    def __init__(self):
        # 初始化事件循环
        self.loop = Loop()
        super().__init__(self)

    # 该类的实例调用 switch 方法启动协程之后将执行 run 方法
    def run(self):
        self.loop.run()


# 全局单例，该实例为协程对象，是 Crawler 实例的 fetch 协程的父协程
hub = Hub()


class Crawler:
    def __init__(self, url):
        self._url = url
        self.url = urlparse(url)
        self.response = b''

    def fetch(self):
        global stopped
        sock = socket.socket()
        sock.setblocking(False)
        try:
            # 向服务器发送连接请求
            sock.connect((self.url.netloc, 80))
        except BlockingIOError:
            pass
        # 这两个参数将在 loop.io 方法内部生成 Watcher 类的实例时作为参数
        # Watcher 类初始化时会注册监听套接字的写事件
        hub.loop.io(sock.fileno(), EVENT_WRITE)
        # 爬虫协程的工作告一段落，等待连接被建立，切换到 hub 协程
        hub.switch()
        # 与服务器连接成功后，套接字的写事件就绪，切换回爬虫协程继续向下执行
        value = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n' \
                .format(self.url.path, self.url.netloc)
        # 向服务器发送数据
        sock.send(value.encode())
        while True:
            # 同上，注册监听套接字的读事件
            # 注意 while 每次循环都会向 loop 对象的 watchers 列表中添加 Watcher 实例
            hub.loop.io(sock.fileno(), EVENT_READ)
            # 爬虫协程的工作告一段落，等待服务器返回数据，切换到 hub 协程
            hub.switch()
            # 服务器返回数据后，套接字可读事件就绪，切换回爬虫协程继续向下执行
            # 接收服务端返回的数据片段
            chunk = sock.recv(4096, 0)
            if chunk:
                self.response += chunk
            else:
                sock.close()
                urls.remove(self._url)
                if not urls:
                    stopped = True
                with open('pic' + self.url.path, 'wb') as file:
                    file.write(self.response.split(b'\r\n\r\n')[1]) 
                print("URL: {0} 下载完成".format(self._url))
                break


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
        # 初始化爬虫实例
        crawler = Crawler(url)
        # 将爬虫实例的 fetch 方法生成协程
        spawn(crawler.fetch)
    # 开始启动 hub 协程
    hub.switch()
    print('程序运行耗时：{:.3f}s'.format(time.time() - start))


if __name__ == '__main__':
    main()