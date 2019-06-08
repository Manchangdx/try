import time
from socket import socket, AF_INET, SOCK_STREAM

ADDR = ('', 1234)
tcp_server_sock = socket(AF_INET, SOCK_STREAM)
tcp_server_sock.setblocking(False)
tcp_server_sock.bind(ADDR)
tcp_server_sock.listen()

print('Waiting for connection...')
while True:
    try:
        try:
            tcp_extension_sock, addr = tcp_server_sock.accept()
        except BlockingIOError:
            continue
    except KeyboardInterrupt:
        break
    print('...connected from {}'.format(addr))
    while True:
        try:
            data = tcp_extension_sock.recv(1024)
        except BlockingIOError:
            continue
        if not data:
            break
        print('收到消息：{}'.format(data.decode()))
        tcp_extension_sock.send('{} {}'.format(
            time.ctime(), data.decode()).encode())
    tcp_extension_sock.close()
tcp_server_sock.close()
