import time
from socket import socket, AF_INET, SOCK_STREAM
  
# HOST 变量是空白的，这是对 bind 方法的标识，表示它可以使用任何可用的地址
HOST = ''
# 选择一个随机的未被占用的端口号
PORT = 21567
# 将缓冲区大小设置为 1KB
BUFSIZ = 1024
# 主机端口元组
ADDR = (HOST, PORT)
 
# 定义 TCP 服务器套接字
tcp_server_sock = socket(AF_INET, SOCK_STREAM)
# 将地址绑定到套接字上
tcp_server_sock.bind(ADDR)
# 开启服务器监听，在连接被转接或拒绝之前，传入连接请求的最大数是 5
tcp_server_sock.listen(5)
 
# 进入监听状态后，等待客户端连接
while True:
    print('Waiting for connection...')
    # 下一行为阻塞运行状态，等待客户端的连接
    # 服务器套接字相当于总机接线员，接到客户电话后转给分机客服
    # 当成功接入一个客户端，accept 方法会返回一个临时服务端套接字和对方地址
    tcp_extension_sock, addr = tcp_server_sock.accept()
    # 如果此时另一个客户端向服务器发送连接请求，也是可以的
    # 请求数由 listen 方法的参数决定
    # 连接成功后保持等待，前一个已连接的客户端断开连接后，才会处理下一个
    print('...connected from: {}'.format(addr))
    while True:
        # 临时服务端套接字的 recv 方法获得客户端传来的数据
        # 此方法也是阻塞运行，每次接收固定量的数据，直到全部接收完毕
        data = tcp_extension_sock.recv(BUFSIZ)
        if not data:
            break
        # 临时服务端套接字的 send 方法向客户端发送数据
        # data 为二进制对象，将其转换为 UTF-8 格式，再整体转换为二进制对象
        tcp_extension_sock.send('{} {}'.format(
            time.ctime(), data.decode()).encode())
    # while 循环结束后，关闭临时服务器套接字
    tcp_extension_sock.close()
tcp_server_sock.close()
