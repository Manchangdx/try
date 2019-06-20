import time
import socket
from urllib.parse import urlparse

# 需要爬取图片的地址列表
urls = ['https://dn-simplecloud.shiyanlou.com/ncn1.jpg',
        'https://dn-simplecloud.shiyanlou.com/ncn110.jpg',
        'https://dn-simplecloud.shiyanlou.com/ncn109.jpg',
        'https://dn-simplecloud.shiyanlou.com/1548126810319.png',
        'https://dn-simplecloud.shiyanlou.com/1517282865454.png'
]


# 定义一个爬虫类
class Crawler:
    def __init__(self, url):
        self.url = url          # 定义该属性，方便后续使用
        self.response = b''     # 该属性用来保存从服务器接收的二进制数据

    def fetch(self):
        # urlparse 方法用来处理 URL ，其返回值便于获得域名和路径
        url = urlparse(self.url)
        # 创建 socket 实例
        self.sock = socket.socket()
        # 该方法阻塞运行，直到成功连接服务器，Web 服务器端口通常为 80
        self.sock.connect((url.netloc, 80))
        print('连接成功')
        # 向服务器发送数据的固定格式
        data = 'GET {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format(
            url.path, url.netloc)
        # 向服务器发送数据，阻塞运行
        self.sock.send(data.encode())
        # 接收服务器返回的数据，阻塞运行
        while True:
            # 每次接收 1K 数据
            d = self.sock.recv(1024)
            if d:
                self.response += d
            else:
                break
        print('接收数据成功')
        # 第一个参数为文件名，注意 url.path 的值的第一个字符为斜杠，须去掉
        # 从服务器接收到的数据为二进制，其中第一部分为报头，第二部分为图片数据
        # 两部分之间使用 \r\n\r\n 隔开，选择第二部分存入文件
        with open(url.path[1:], 'wb') as f:
            f.write(self.response.split(b'\r\n\r\n')[1])
        print('保存文件成功')
        self.sock.close()

def main():
    start = time.time()
    for url in urls:
        # 创建爬虫实例
        crawler = Crawler(url)
        # 开始爬取数据
        crawler.fetch()
    print('耗时：{:.2f}s'.format(time.time() - start))

if __name__ == '__main__':
    main()
