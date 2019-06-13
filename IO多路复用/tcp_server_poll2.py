import select
import socket
import time

sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.setblocking(False)
sock_server.bind(('', 1234))
sock_server.listen()

connections = {}    # 存放新建临时分支套接字
p = select.poll()   # 创建 poll 对象
# 将主套接字 sock_server 的文件描述符注册到读事件链表里
# poll 对象的 register 方法接收俩参数：套接字的文件描述符、链表类型
# 针对套接字的仨事件：POLLIN 可读，POLLOUT 可写，POLLHUP 关闭
p.register(sock_server.fileno(), select.POLLIN)
print('server listening !!!')
while True:
    print('============循环============')
    # 获取发生事件的文件描述符
    for fd, event in p.poll():
        print('-------------- 套接字FD: {} event: {}'.format(fd, event))
        print('-------------- connections: {}'.format(connections))
        print('--------------', select.POLLIN)
        print('--------------', select.POLLOUT)
        print('--------------', select.POLLHUP)
        # 如果主套接字有情况，一定是读事件，它只管接收客户端连接
        if fd == sock_server.fileno():
            # 接收客户端的连接，会创建新的套接字，用来处理发送和接收数据
            extension_server, addr = sock_server.accept()
            print('Accept connection:', addr)
            # 将新的套接字设置为非阻塞的
            extension_server.setblocking(0)
            # 将新的连接注册读事件，用来读取客户端的数据
            p.register(extension_server.fileno(), select.POLLIN)
            # 把新建临时分支套接字加入到字典里
            connections[extension_server.fileno()] = extension_server
        # 如果发生可读事件，也就是说已连接的客户端发送数据过来
        elif event & select.POLLIN:
            # 根据文件描述符，获取发生读事件的临时套接字
            conn = connections[fd]
            # 开始接收数据
            data = conn.recv(1024)
            if data:
                print('收到数据: ', data.decode())
            # 将注册的事件修改为可写事件，向客户端发送数据
            p.modify(fd, select.POLLOUT)
        # 如果发生写事件，也就是临时套接字处理完客户端发来的信息后，回信息
        elif event & select.POLLOUT:
            print("向客户端发送数据...")
            # 获取发生写事件的socket对象
            conn = connections[fd]
            # 开始发送数据
            conn.send('收到信息，这是模拟信息'.encode())
            # 关闭socket连接
            conn.shutdown(socket.SHUT_RDWR)
        # 如果发生关闭事件
        elif event & select.POLLHUP:
            print('event POLLHUP')
            # 注销文件描述符，不再接收事件
            p.unregister(fd)
            # 关闭连接
            connections[fd].close()
            # 从socket对象集中删除
            del connections[fd]
print('\nClose ...', sock_server.fileno())
# 注销sock_server
p.unregister(sock_server.fileno())
# 关闭连接
sock_server.close()
