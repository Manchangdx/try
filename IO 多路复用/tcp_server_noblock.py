import time
from socket import socket, AF_INET, SOCK_STREAM

ADDR = ('', 1234)
tcp_server_sock = socket(AF_INET, SOCK_STREAM)
tcp_server_sock.setblocking(False)  # 设置非阻塞，注意是系统调用非阻塞
tcp_server_sock.bind(ADDR)
tcp_server_sock.listen()

print('Waiting for connection...')
while True:
    try:
        try:
            # 设置非阻塞后，套接字的 accept 方法进行系统调用后立即返回
            # accept 方法会触发 BlockingIOError 异常
            # 捕获这个异常，继续 while 循环，直到系统空间收到客户端连接
            tcp_extension_sock, addr = tcp_server_sock.accept()
        except BlockingIOError:
            continue
    except KeyboardInterrupt:
        break
    print('------ connected from {}'.format(addr))
    while True:
        try:
            # 同上，设置非阻塞后，套接字的 recv 方法进行系统调用后立即返回
            # recv 方法会触发 BlockingIOError 异常
            # 捕获这个异常，继续 while 循环，直到系统空间收到客户端消息
            data = tcp_extension_sock.recv(1024)
        except BlockingIOError:
            continue
        if not data:
            break
        print('收到消息：{}'.format(data.decode()))
        tcp_extension_sock.send('{} {}'.format(
            time.ctime(), data.decode()).encode())
    print('------ {} connection closed.'.format(addr))
    tcp_extension_sock.close()
print('\nEnd')
tcp_server_sock.close()
