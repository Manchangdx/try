import time
import select
from socket import socket, AF_INET, SOCK_STREAM

ADDR = ('', 1234)
tcp_server_sock = socket(AF_INET, SOCK_STREAM)
tcp_server_sock.setblocking(False)
tcp_server_sock.bind(ADDR)
tcp_server_sock.listen()
print(dir(tcp_server_sock))
rlist = [tcp_server_sock]   # 这三个列表作为 select.select 的参数
wlist = []
xlist = []

print('Waiting for connection...')

# 这个 while 循环是核心
# 每当有客户端发起连接请求、关闭连接、发送消息，这块儿 while 都会循环一次
while True:
    print('--------------------')
    # 套接字的 fileno 方法的返回值就是其文件描述符，一个正整数
    # 在一个进程中，每个套接字都有独一无二且固定不变的文件描述符
    print('rlist:', ['套接字FD: {}'.format(s.fileno()) for s in rlist])
    print('wlist:', ['套接字FD: {}'.format(s.fileno()) for s in wlist])
    try:
        # select.select 方法阻塞运行，直到三个参数列表里的套接字有情况出现
        # 所谓的有情况，就是套接字文件描述符准备就绪，可读、可写、异常
        # 在一个线程内，此方法可以监视上千个描述符，比多线程模式节省大量 CPU 开销
        # 此方法的返回值是元组，元组里是三个列表，列表里是有情况的套接字
        t = select.select(rlist, wlist, xlist)
        readable, writable, exceptional = t
        print('readable:', ['套接字FD: {}'.format(s.fileno()) for s in readable])
        print('writable:', ['套接字FD: {}'.format(s.fileno()) for s in writable])
    except KeyboardInterrupt:
        break

    # 处理有情况的可读套接字
    for sock in readable:
        # TCP 服务端的套接字有两种，一种是等待客户端连接的主套接字
        # 另一种是负责处理连接后的一系列事务的分支套接字
        # 如果是主套接字有情况，甭问，肯定是有客户端连接请求，它就是干这个的
        # 这种情况，主套接字的 accept 方法会返回一个新建分支套接字
        if sock is tcp_server_sock:
            tcp_extension_sock, addr = sock.accept()
            print('收到连接：{}'.format(addr))
            # 把分支套接字设为非阻塞，注意是系统调用那块儿的非阻塞
            tcp_extension_sock.setblocking(False)
            # 把分支套接字加到作为 select.select 方法的参数的列表里
            rlist.append(tcp_extension_sock)
        # 如果有情况的不是主套接字，那就是分支套接字了
        # 肯定是客户端发来消息了，接收消息
        # 接收完毕，该套接字自动可写就绪，也就是要把它放到 wlist 列表里
        # 下一个 while 循环就处理这个可写套接字
        else:
            data = sock.recv(1024)
            if data:
                print('收到数据：{}'.format(data.decode()))
                if sock not in wlist:
                    wlist.append(sock)
            else:
                # 如果消息接收完毕，移除分支套接字并关闭
                rlist.remove(sock)
                sock.close()

    # 处理有情况的可写套接字
    for sock in writable:
        print('Server send ...')
        sock.send('{}'.format(time.ctime()).encode())
        # 处理完，把套接字移除 wlist 
        wlist.remove(sock)

    # 处理有情况的异常套接字
    for sock in exceptional:
        print('Exceptional sock', sock)
        rlist.remove(sock)
        if sock in wlist:
            wlist.remove(sock)
        sock.close()

    print('====================')
print('\nEnd')
tcp_server_sock.close()
