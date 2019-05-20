import itertools
import time
import asyncio
import sys

@asyncio.coroutine
def spin():
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' calculating!'
        write(status)
        flush()
        write('\x08' * len(status))
        try:
            # 这个小休眠会将 CPU 释放，转而运行外层协程 supervisor 中的代码
            yield from asyncio.sleep(.1)
        except asyncio.CancelledError:
            break
    write(' ' * len(status) + '\x08' * len(status))

@asyncio.coroutine
def slow():
    # time.sleep 会阻塞整个进程
    # asyncio.sleep 仅阻塞当前协程，不会阻塞 loop 事件循环
    yield from asyncio.sleep(3) 
    return 123

@asyncio.coroutine
def supervisor():
    print('开始转圈...')
    # asyncio.ensure_future 接收协程作为参数返回任务对象
    # 将协程 spin 注入 future 生成任务
    spinner = asyncio.ensure_future(spin()) 
    # 休眠 3 秒后，将协程 slow 的返回值赋值给 result
    # 在休眠过程中，CPU 被释放，处理 spinner 任务
    result = yield from slow()              
    # 任务的 cancel 方法触发 asyncio.CancelledError 异常
    # 在 spin 协程中捕获该异常，这就相当于上一版关闭协程的信号
    spinner.cancel()                        
    return result

def main():
    start = time.time()
    loop = asyncio.get_event_loop()     # 创建事件循环
    # 将协程 supervisor 注入事件循环生成任务对象并启动
    # 将协程 supervisor 的返回值赋值给 result
    result = loop.run_until_complete(supervisor())  
    print('Answer: {}'.format(result))
    print('耗时 {:.2f}s'.format(time.time()-start))

if __name__ == '__main__':
    # 整个程序中，main 启动事件循环，里面就 supervisor 一件事
    # supervisor 里一共就两件事，spinner 任务和 slow 休眠
    # 
    main()
