import time
import os
import pyuv
from urllib.parse import urlparse

urls = ['https://dn-simplecloud.shiyanlou.com/ncn1.jpg',
        'https://dn-simplecloud.shiyanlou.com/ncn110.jpg',
        'https://dn-simplecloud.shiyanlou.com/ncn109.jpg',
        'https://dn-simplecloud.shiyanlou.com/1548126810319.png',
        'https://dn-simplecloud.shiyanlou.com/1517282865454.png',
        'https://dn-simplecloud.shiyanlou.com/1543913883545.png',
        'https://dn-simplecloud.shiyanlou.com/1502778396172.png',
        'https://dn-simplecloud.shiyanlou.com/1540965522764.png',
        'https://dn-simplecloud.shiyanlou.com/1546500900109.png',
        'https://dn-simplecloud.shiyanlou.com/1547620906601.png'
]


class Crawler:
    # 初始化，参数 loop 是 pyuv 生成的事件循环对象
    def __init__(self, url, loop):
        self._url = url
        self.url = urlparse(self._url)
        self.response = b''
        self.loop = loop

    def fetch(self):
        # 使用 DNS 解析域名，获取图片服务器相关信息
        addrinfo = pyuv.dns.getaddrinfo(self.loop, self.url.netloc)
        if not addrinfo:
            print('图片地址不正确')
            return
        # 图片服务器 IP 地址
        ip = addrinfo[-1].sockaddr[0]   
        # 参数 self.loop 会自动选用平台上最优的 I/O 模型创建 TCP 客户端
        client = pyuv.TCP(self.loop)    
        # 向服务器发送连接请求，self.writable 方法作为回调函数
        client.connect((ip, 80), self.writable)

    # 该方法为回调函数，连接服务器成功后自动被调用
    # handler 和 error 为 pyuv 调用该回调函数时所需参数，不需要我们提供
    # handler 是对 socket 的封装，提供相同功能的读写接口
    def writable(self, handler, error):
        try:
            data = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close' \
                    '\r\n\r\n'.format(self.url.path, self.url.netloc)
            # 向服务器发送请求数据，并提供回调函数用于接收服务器传回的数据
            handler.write(data.encode(), self.readable)
        except Exception as e:
            print(e)

    # 当服务器传回数据时，客户端套接字可读事件就绪，自动运行此回调函数
    def readable(self, handler, error):
        # start_read 方法处理传回的数据
        # 此方法只提供一个参数，这个参数为嵌套函数，会被自动调用
        # get_data 为嵌套回调函数，用于处理数据
        handler.start_read(self.get_data)

    # 该方法亦为被动调用的回调函数，用于处理服务器返回的数据
    # handler 为 socket 的封装，可以看作客户端套接字
    # data 为服务器返回的数据片段
    def get_data(self, handler, data, error):
        # 客户端套接字未关闭时，其可读事件一直被监听
        if data:
            self.response += data
        # 数据接收完毕，将客户端套接字关闭
        else:
            handler.close()
            # 将图片数据写入文件
            with open('pic' + self.url.path, 'wb') as file:
                file.write(self.response.split(b'\r\n\r\n')[1])
            print(self.url.path[1:], '已保存')


def main():
    start = time.time()
    os.system('mkdir -p pic')
    # 创建 loop 事件循环对象，pyuv 自动选择系统中性能最好的 I/O 模型
    # Linux 平台会选用 epoll 模型，BSD/macOS 平台选用 kqueue 模型
    loop = pyuv.Loop.default_loop()
    for url in urls:
        crawler = Crawler(url, loop)
        crawler.fetch()
    # 启动事件循环，和之前实现的事件循环原理差不多
    # 但做了更多的优化处理和封装，简化了代码
    loop.run()
    print('程序运行总耗时：{:.3f}s'.format(time.time() - start))


if __name__ == '__main__':
    main()
