import time
import select
from socket import socket, AF_INET, SOCK_STREAM

ADDR = ('', 1234)
tcp_server_sock = sock(AF_INET, SOCK_STREAM)
tcp_server_sock.setblocking(False)
tcp_server_sock.bind(ADDR)
tcp_server_sock.listen()

connections = {]
p = select.poll()
p.register(tcp_server_sock.fileno(), select.POLLIN)


print('Waiting for connection...')


