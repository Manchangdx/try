import threading
import itertools
import time

def 转圈():
    for char in itertools.cycle('|/-\\'):              # 无限循环
        msg = char + ' Pretending to calculate!'       # 打印到屏幕的msg
        print(msg, flush=True, end='')                 # 打印 / 覆盖
        print('\x08' * len(msg), flush=True, end='')   # 回退
        time.sleep(0.1)
        if signal:
            break
    # 用空格覆盖，然后回退
    print(' ' * len(msg) + '\x08' * len(msg), flush=True, end='')

def main():
    global signal
    signal = 0
    线程 = threading.Thread(target=转圈)
    print('启动线程，开始转圈~')
    线程.start()
    time.sleep(3)   # 假装计算 3 秒，sleep 阻塞子线程，释放 CPU
    signal = 1      # 修改这个值，影响子线程中的调用
    线程.join()
    print('计算结果: 6524')

if __name__ == '__main__':
    main()
