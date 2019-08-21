import time
import threading
from socket import socket, AF_INET, SOCK_STREAM

ADDR = ('', 1234)
tcp_server_sock = socket(AF_INET, SOCK_STREAM)
tcp_server_sock.bind(ADDR)
tcp_server_sock.listen()

def handle(sock, addr):
    while True:
        data = sock.recv(1024).decode()
        if not data:
            sock.close()
            break
        print('收到消息：{}'.format(data))
        sock.send('{} {}'.format(
            time.ctime(), data).encode())
    print('已关闭端口：{}'.format(addr[-1]))

def main():
    print('等待客户端请求...')
    while True:
        try:
            sock, addr = tcp_server_sock.accept()
            print('已连接端口：{}'.format(addr[-1]))
        except KeyboardInterrupt:
            break
        t = threading.Thread(
            target=handle, args=(sock, addr))
        t.start()
    print('\nExit')
    tcp_server_sock.close()

if __name__ == '__main__':
    main()
