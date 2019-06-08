import time
import select
from socket import socket, AF_INET, SOCK_STREAM

ADDR = ('', 1234)
tcp_server_sock = socket(AF_INET, SOCK_STREAM)
tcp_server_sock.setblocking(False)
tcp_server_sock.bind(ADDR)
tcp_server_sock.listen()
rlist = [tcp_server_sock]
wlist = []
xlist = []

print('Waiting for connection...')
while True:
    print('--------------------')
    print('rlist:', rlist)
    print('wlist:', wlist)
    try:
        l = select.select(rlist, wlist, xlist)
        readable, writable, exceptional = l
        print('readable:', readable)
        print('writable:', writable)
    except KeyboardInterrupt:
        break

    for sock in readable:
        if sock is tcp_server_sock:
            tcp_extension_sock, addr = sock.accept()
            print('收到连接：{}'.format(addr))
            tcp_extension_sock.setblocking(False)
            rlist.append(tcp_extension_sock)
        else:
            data = sock.recv(1024)
            if data:
                print('收到数据：{}'.format(data.decode()))
                if sock not in wlist:
                    wlist.append(sock)
            else:
                rlist.remove(sock)
                sock.close()

    for sock in writable:
        print('Server send ...')
        sock.send('{}'.format(time.ctime()).encode())
        wlist.remove(sock)

    for sock in exceptional:
        print('Exceptional sock', sock)
        rlist.remove(sock)
        if sock in wlist:
            wlist.remove(sock)
        sock.close()

    print('====================')
print('\nOVER')
tcp_server_sock.close()
