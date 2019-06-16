import select
import socket
import time

# Linux 平台使用 select.epoll 接口，将其封装为 Epoll 类
class Epoll():
    def __init__(self,):
        # 初始化实例时，创建 epoll 对象，等同于 poll 对象
        self._epoll = select.epoll()    # edge polling 边缘轮询对象

    # 获取文件描述符，这个方法在该程序中没有用到
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
        # epoll 对象的 poll 方法的作用等同于 poll 的 poll 方法
        # 监听已注册的套接字，该方法阻塞运行
        # 直到有事件就绪，返回就绪事件的列表
        events = self._epoll.poll(timeout)
        # 这个字典用来保存处理后的就绪事件
        events_ = {}
        # 就绪事件为何要处理？因为 epoll 与 kqueue 所提供的事件位掩码不同
        # 所以统一改成 poll 提供的事件位掩码
        for fd, flag in events:
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

# Mac OS 平台使用 select.kqueue 接口，将其封装为 Kqueue 类
# kqueue 的接口和 poll 的接口相差比较大
class Kqueue():
    def __init__(self):
        # 初始化实例时，创建 kqueue 对象，等同于 poll 对象
        self._kqueue = select.kqueue()  # kernel queue 内核队列对象
        # 保存被监听的临时套接字的字典，这个在 poll 和 epoll 里没有
        # 它的作用是避免重复监视同一个套接字事件
        self._active = {}

    # 获取文件描述符，这个方法在该程序中没有用到
    def fileno(self):
        return self._kqueue.fileno()

    # 注册临时套接字，监听某种事件，参数为文件描述符和事件位掩码
    def register(self, fd, flag):
        if fd not in self._active:
            # _control 方法监听套接字的某种事件，参数为 KQ_EV_ADD 
            self._control(fd, flag, select.KQ_EV_ADD)
            self._active[fd] = flag

    # 注销文件描述符，不再监听对应的套接字事件
    def unregister(self, fd):
        events = self._active.pop(fd)
        self._control(fd, events, select.KQ_EV_DELETE)

    # 修改文件描述符注册的事件
    # kqueue 没有 modify 方法，通过先注销再注册事件实现
    def modify(self, fd, flag):
        self.unregister(fd)
        self.register(fd, flag)

    # 该自定义方法使用 kqueue.control 方法来添加和删除事件监听
    # 参数为套接字的文件描述符、事件位掩码、行为常数
    # 行为常数有很多，这里用到两个：
    # KQ_EV_ADD 值为 1 ，添加监听；KQ_EV_DELETE 值为 2 ，撤销监听
    def _control(self, fd, flag, flags):
        kevents = []
        # 如果事件位掩码匹配可读
        if flag & select.POLLIN:
            # select.kevent 方法的返回值是内核事件，也就是需要添加或删除的事件
            # 把返回值添加到 kevents 列表，后面使用 kqueue 的 control 方法处理
            # 该方法的参数：套接字的文件描述符、过滤常数、行为常数
            # 过滤常数是负整数，添加可读事件监听使用 select.KQ_FILTER_READ
            # 其作用跟 poll.register 中的 select.POLLIN 是一样的
            kevents.append(select.kevent(
                fd, filter = select.KQ_FILTER_READ, flags=flags))
        # 如果事件位掩码匹配可写
        if flag & select.POLLOUT:
            kevents.append(select.kevent(
                fd, filter = select.KQ_FILTER_WRITE, flags=flags))
        for kevent in kevents:
            # control 方法处理 kevent 列表里的所有事件
            # 第一个参数为内核事件的可迭代对象
            # 第二个参数是最大事件数，必须是 0 或正整数
            # 第二个参数如果为负会抛出异常，固定值 0 表示无限制
            # 第三个参数 timeout 没有写
            self._kqueue.control([kevent], 0)

    # 监听事件，获取发生事件的文件描述符
    def poll(self, timeout=None):
        # kqueue 对象的 control 方法等同于 poll 的 poll 方法
        # 监听已注册的套接字，该方法阻塞运行
        # 直到有事件就绪，返回就绪事件的列表 kevents ，这和上面的 epoll 一样
        kevents = self._kqueue.control(None, 1000, timeout)
        # 这个字典用来保存处理后的就绪事件
        events_ = {}
        # 同 epool 一样，处理就绪事件是为了统一事件位掩码
        for kevent in kevents:
            # kevent.ident 为事件标识，属性值为对应的文件描述符
            fd = kevent.ident   
            # kevent.filter 为过滤标识，属性值为过滤常数
            if kevent.filter == select.KQ_FILTER_READ:
                events_[fd] = events_.get(fd, 0) | select.POLLIN
            if kevent.filter == select.KQ_FILTER_WRITE:
                events_[fd] = events_.get(fd, 0) | select.POLLOUT
        return events_.items()

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
            # 注册新的临时套接字，监听其可读事件
            p.register(extension_sock.fileno(), select.POLLIN)
            # 把新建临时分支套接字加入到存储连接的字典里
            connections[extension_sock.fileno()] = extension_sock

        # 如果临时套接字可读事件就绪，也就是客户端发来数据
        elif flag & select.POLLIN:
            # 利用文件描述符从 connections 里获取对应的临时套接字
            extension_sock = connections[fd]
            # 接收数据这块儿需要注意，如果客户端突然关闭连接
            # 对应的临时套接字会可读就绪，即事件位掩码为 1
            data = extension_sock.recv(1024)
            if data:
                print('套接字 {} 收到数据: {}'.format(fd, data.decode()))
                # 套接字收到数据后，可写事件立即就绪
                # 转而监听其可写事件，下个 while 循环会处理
                p.modify(fd, select.POLLOUT)
            else:
                # 如果收到的数据是 None ，可能客户端已关闭，连接已断开
                # 注销文件描述符对应的套接字，不再监听相关事件
                p.unregister(fd)
                # 关闭套接字
                extension_sock.close()
                # 将套接字从 connections 里移出
                del connections[fd]
                print('套接字 {} 已关闭'.format(fd))

        # 如果套接字可写事件就绪
        if flag & select.POLLOUT:
            print("套接字 {} 发送数据...".format(fd))
            extension_sock = connections[fd]
            # 向客户端发送数据
            extension_sock.send('收到信息，这是模拟信息'.encode())
            # 套接字向客户端发送消息后，poll 转为监听其可读事件
            p.modify(fd, select.POLLIN)

        # 如果客户端关闭，临时套接字的关闭事件会就绪
        # 注意，关闭事件无法使用 poll.modify 方法主动设置，只能被触发
        if flag & select.POLLHUP:
            print('套接字 {} 已关闭'.format(fd))
            # 注销文件描述符对应的套接字，不再监听相关事件
            p.unregister(fd)
            # 关闭套接字
            extension_sock.close()
            # 将套接字从 connections 里移出
            del connections[fd]

    print('--------connections: {}'.format(list(connections.keys())))
    print('========循环结束========')

# 撤销对主套接字的事件监听
p.unregister(server_sock.fileno())
# 关闭系统调用对象
p.close()
# 关闭主套接字服务端
server_sock.close()
print('\nEnd')
