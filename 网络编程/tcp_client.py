from socket import socket, AF_INET, SOCK_STREAM

ADDR = ('localhost', 1234)
tcp_client_sock = socket(AF_INET, SOCK_STREAM)
tcp_client_sock.connect(ADDR)

while True:
    data = input('输入内容：')
    if not data:
        break
    tcp_client_sock.send(data.encode())
    data = tcp_client_sock.recv(1024)
    if not data:
        break
    print(data.decode())

tcp_client_sock.close()
