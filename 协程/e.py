import itertools
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
            yield from asyncio.sleep(.1)
        except asyncio.CancelledError:
            break
    write(' ' * len(status) + '\x08' * len(status))

@asyncio.coroutine
def slow():
    yield from asyncio.sleep(3)
    return 123

def main():
    print('开始转圈...')
    #loop = asyncio.get_event_loop()         # 创建事件循环
    #spinner = asyncio.ensure_future(spin()) # 将协程 spin 注入 future 生成任务
    # 将协程 supervisor 注入事件循环生成任务对象并启动
    # loop.run_until_complete(spinner)  
    result = yield from slow()              # 将协程 slow 的返回值赋值给 result
    # 任务的 cancel 方法触发 asyncio.CancelledError 异常
    # spin 协程中捕获该异常，这就相当于上一版关闭协程的信号
    #spinner.cancel()                        
    #print('Answer: {}'.format(result))

if __name__ == '__main__':
    main()
