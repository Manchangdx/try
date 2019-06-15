import select
import socket
import time

# Linux 平台使用 select.epoll 接口，将其封装为 Epoll 类
class Epoll():
    def __init__(self,):
        self._epoll = select.epoll()

    # 获取文件描述符
    def fileno(self):
        return self._epoll.fileno()

    # 注册临时套接字，监听某种事件，参数为文件描述符和事件位掩码
    def register(self, fd, flag):
        self._epoll.register(fd, flag)

    # 注销临时套接字，参数为文件描述符
    def unregister(self, fd):
        self._epoll.unregister(fd)

    # 修改临时套接字的监听事件类型
    def modify(self, fd, flag):
        self._epoll.modify(fd, flag)

    def poll(self, timeout=None):
        # 监听已注册的套接字，该方法为阻塞运行，直到有事件就绪
        # 获取就绪事件列表
        events = self._epoll.poll(timeout)
        # 这个字典用来保存处理后的就绪事件
        events_ = {}
        # 因为 epoll 与 kqueue 所提供的事件位掩码不同
        # 所以统一改成 poll 提供的事件位掩码
        for fd, flag in events:
            print('((((((((((((((((', flag)
            # 可读事件就绪
            if flag & select.EPOLLIN:
                # 将事件位掩码转换为 POLLIN
                events_[fd] = events_.get(fd, 0) | select.POLLIN
            # 可写事件就绪
            if flag & select.EPOLLOUT:
                # 将事件位掩码转换为 POLLOUT
                events_[fd] = events_.get(fd, 0) | select.POLLOUT
            # 关闭事件就绪
            if flag & select.EPOLLHUP:
                # 将事件位掩码转换为 POLLOUT
                events_[fd] = events_.get(fd, 0) | select.POLLHUP
        return events_.items()

# 封装kqueue对象，Mac平台调用
# kqueue的接口和poll的接口相差比较大
class Kqueue():

    # 初始化kqueue对象
    def __init__(self):
        # 使用kqueue
        self._kqueue = select.kqueue()
        self._active = {}

    def fileno(self):
        return self._kqueue.fileno()

    # 注册文件描述符的事件
    def register(self, fd, events):
        if fd not in self._active:
            # 注册事件，使用KQ_EV_ADD标志
            self._control(fd, events, select.KQ_EV_ADD)
            self._active[fd] = events

    # 注销文件描述符
    def unregister(self, fd):
        events = self._active.pop(fd)
        self._control(fd, events, select.KQ_EV_DELETE)

    # 修改文件描述符注册的事件
    # kqueue没有modify方法，通过先注销，再注册事件实现
    def modify(self, fd, events):
        self.unregister(fd)
        self.register(fd, events)

    # 进行事件注册，主要是调用kqueue的control方法
    def _control(self, fd, events, flags):
        kevents = []
        # 文件描述符注册事件
        if events & select.POLLIN:
            kevents.append(select.kevent(
                fd, filter=select.KQ_FILTER_READ, flags=flags))
        if events & select.POLLOUT:
            kevents.append(select.kevent(
                fd, filter=select.KQ_FILTER_WRITE, flags=flags))
        for kevent in kevents:
            self._kqueue.control([kevent], 0)

    # 监听事件，获取发生事件的文件描述符
    def poll(self, timeout=None):
        kevents = self._kqueue.control(None, 1000, timeout)
        events = {}
        for kevent in kevents:
            fd = kevent.ident
            if kevent.filter == select.KQ_FILTER_READ:
                events[fd] = events.get(fd, 0) | select.POLLIN
            if kevent.filter == select.KQ_FILTER_WRITE:
                events[fd] = events.get(fd, 0) | select.POLLOUT
        return events.items()

    def close(self):
        self._kqueue.close()

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setblocking(False)
server_sock.bind(('localhost', 1234))
server_sock.listen()
print('server listening !!!')

connections = {}
# 根据不同平台使用对应的接口
if hasattr(select, 'epoll'):
    print('Linux')
    p = Epoll()
elif hasattr(select, 'kqueue'):
    print('Mac OS')
    p = Kqueue()
# server_sock注册读事件
p.register(server_sock.fileno(), select.POLLIN)

while True:
    time.sleep(1)
    print('\n========循环开始========')
    try:
        events = p.poll()
    except KeyboardInterrupt:
        break

    # 获取发生事件的文件描述符和相应的事件
    for fd, flag in events:
        print('--------套接字FD: {} 位掩码: {}'.format(fd, flag))

        # 如果主套接字有事件就绪，一定是可读就绪，它只负责接收客户端连接
        if fd == server_sock.fileno():
            # 接收客户端的连接请求，创建新的临时套接字用来发送和接收数据
            extension_sock, addr = server_sock.accept()
            print('收到连接，客户端地址:', addr)
            # 将新的临时套接字设置为非阻塞模式
            extension_sock.setblocking(0)
            # 注册新的临时套接字，监视其可读事件
            p.register(extension_sock.fileno(), select.POLLIN)
            # 把新建临时分支套接字加入到存储连接的字典里
            connections[extension_sock.fileno()] = extension_sock

        # 如果临时套接字可读事件就绪，也就是客户端发来数据
        elif flag & select.POLLIN:
            # 利用文件描述符从 connections 里获取对应的临时套接字
            extension_sock = connections[fd]
            # 接收数据这块儿需要注意，如果客户端突然关闭连接
            # 对应的临时套接字会同时可读和关闭就绪，即事件位掩码为 17
            # 此时套接字的 recv 方法在运行时会触发 ConnectionResetError 异常
            # 捕获这个异常，使程序向下执行，顺利关闭套接字
            try: 
                data = extension_sock.recv(1024)
            except ConnectionResetError:
                pass
            if data:
                print('套接字 {} 收到数据: {}'.format(fd, data.decode()))
                # 套接字收到数据后，可写事件立即就绪
                # 转而监视其可写事件，下个 while 循环会处理
                p.modify(fd, select.POLLOUT)
            else:
                print('LLLLLLLLLLLLLLLLLLLL')
                p.modify(fd, select.POLLOUT)

        # 如果套接字可写事件就绪
        if flag & select.POLLOUT:
            print("套接字 {} 发送数据...".format(fd))
            extension_sock = connections[fd]
            # 向客户端发送数据
            extension_sock.send('收到信息，这是模拟信息'.encode())
            # 套接字向客户端发送消息后，poll 转为监视其可读事件
            p.modify(fd, select.POLLIN)

        # 如果客户端关闭，临时套接字的关闭事件会就绪
        if flag & select.POLLHUP:
            print('套接字 {} 关闭'.format(fd))
            # 注销文件描述符对应的套接字，不再监视相关事件
            p.unregister(fd)
            # 关闭套接字
            extension_sock.close()
            # 将套接字从 connections 里移出
            del connections[fd]

    print('--------connections: {}'.format(list(connections.keys())))
    print('========循环结束========')

p.unregister(server_sock.fileno())
# 关闭服务端
server_sock.close()
print('\nEnd')
