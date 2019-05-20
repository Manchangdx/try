# File Name: pro_con.py

def consumer():
    r = ''
    while True:
        n = yield r
        print('[CONSUMER] Consuming {}'.format(n))
        r = '200 OK'


def producer(c):
    c.send(None)    # 等同于 next(c) ，预激协程
    n = 0 
    while n < 3:
        n += 1
        print('[PRODUCER] Producing {}'.format(n))
        r = c.send(n)
        print('[PRODUCER] Consumer return: {}'.format(r))
    c.close()       # 这行可以不写，程序终止时由 Python 回收未结束的协程


if __name__ == '__main__':
    c = consumer()
    producer(c)
