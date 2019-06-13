import select
import socket
import time

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setblocking(False)
server_sock.bind(('', 1234))
server_sock.listen()

connections = {}      # 存放新建临时分支套接字，key 是文件描述符，value 是套接字
poll = select.poll()  # 创建 poll 对象
# 将主套接字 server_sock 的文件描述符注册到读事件链表里
# poll 对象的 register 方法接收俩参数：套接字的文件描述符、链表类型（事件描述符）
# 针对套接字的仨事件及其描述符（正整数）：
# POLLIN 可读 1 ，POLLOUT 可写 4 ，POLLHUP 关闭 16
poll.register(server_sock.fileno(), select.POLLIN)

print('Waiting for connection...')
while True:
    time.sleep(1)
    print('============循环开始============')
    # 获取发生事件的文件描述符和事件描述符
    try:
        for fd, event in poll.poll():
            print('------------套接字FD: {} event: {}'.format(fd, event))
            # 如果主套接字有情况，一定是读事件，它只管接收客户端连接
            if fd == server_sock.fileno():
                # 接收客户端的连接，会创建新的套接字，用来处理发送和接收数据
                extension_sock, addr = server_sock.accept()
                # print('extension_sock.getpeername: {}'.format(
                #     extension_sock.getpeername()))
                print('Accept connection:', addr)
                # 将新的套接字设置为非阻塞的
                extension_sock.setblocking(0)
                # 将新的连接注册读事件，用来读取客户端的数据
                poll.register(extension_sock.fileno(), select.POLLIN)
                # 把新建临时分支套接字加入到字典里
                connections[extension_sock.fileno()] = extension_sock
            # 如果发生可读事件，也就是说已连接的客户端发送数据过来
            elif event & select.POLLIN:
                # 根据文件描述符，获取发生读事件的临时套接字
                extension_sock= connections[fd]
                # 开始接收数据
                try:
                    data = extension_sock.recv(1024)
                except ConnectionResetError:
                    poll.modify(fd, select.POLLHUP)
                if data:
                    print('从客户端 {} 收到数据: {}'.format(fd, data.decode()))
                    # 将注册的事件修改为可写事件，向客户端发送数据
                    poll.modify(fd, select.POLLOUT)
            # 如果发生写事件，也就是临时套接字处理完客户端发来的信息后，回信息
            elif event & select.POLLOUT:
                print("向客户端 {} 发送数据...".format(fd))
                # 获取发生写事件的socket对象
                extension_sock = connections[fd]
                # 开始发送数据
                extension_sock.send('收到信息，这是模拟信息'.encode())
                # 将注册的事件修改为可写事件，向客户端发送数据
                poll.modify(fd, select.POLLIN)
                # 关闭socket连接
                # extension_sock.shutdown(socket.SHUT_RDWR)
            # 如果发生关闭事件
            elif event & select.POLLHUP:
                print('套接字关闭: {}'.format(connections[fd]))
                # 注销文件描述符，不再接收事件
                poll.unregister(fd)
                # 关闭连接
                connections[fd].close()
                # 从socket对象集中删除
                del connections[fd]
        print('------------connections: {}'.format(connections))
        print('============循环结束============')
    except KeyboardInterrupt:
        break
print('\nEnd')
# 注销server_sock
poll.unregister(server_sock.fileno())
# 关闭连接
server_sock.close()
