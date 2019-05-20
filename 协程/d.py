import time
import asyncio
import functools

# 版本一
def one():
    start = time.time()
    # async 关键字可定义一个协程函数
    # @asyncio.coroutine 这个装饰器也可以定义协程
    # 注意，函数的返回值才是协程，也叫事件
    # 协程不能单独运行，需要作为事件注入到事件循环 loop 里
    async def do_some_work(x):
        time.sleep(.01)
        print('[do_some_work]  这是个协程任务')
        print('[do_some_work]  Coroutine {}'.format(x))
    coroutine = do_some_work('one')     # 创建协程
    loop = asyncio.get_event_loop()     # 创建事件循环
    loop.run_until_complete(coroutine)  # 将协程注入事件循环生成任务对象并启动
    print('----- 运行耗时：{:.4f}s -----'.format(time.time()-start))

# 版本二
def two():  
    start = time.time()
    async def do_some_work(x):
        time.sleep(.01)
        print('[do_some_work]  这是个协程任务')
        print('[do_some_work]  Coroutine {}'.format(x))
    coroutine = do_some_work('two')         # 创建协程
    loop = asyncio.get_event_loop()         # 创建事件循环
    task = loop.create_task(coroutine)      # 将协程作为参数创建任务
    # task = asyncio.ensure_future(coroutine) 作用同上，task 是 Future 类的子类
    print('[task] ', task._state)           # 打印任务状态
    loop.run_until_complete(task)           # 将任务注入事件循环并启动
    print('[task] ', task._state)           # 打印任务状态
    print('----- 运行耗时：{:.4f}s -----'.format(time.time()-start))

one()
two()
# 版本三
def three():
    start = time.time()
    async def do_some_work(x):
        time.sleep(.01)
        print('[do_some_work]  这是个协程任务')
        print('[do_some_work]  Coroutine {}'.format('three'))
    def callback(name, future):             # 回调函数，在任务中被使用
        print('[callback]  回调函数，干点儿别的')
        print('[callback]  {} 状态: {}'.format(name, future._state))
    coroutine = do_some_work(2)             # 创建协程
    loop = asyncio.get_event_loop()         # 创建事件循环
    task = loop.create_task(coroutine)      # 将协程作为参数创建任务
    print('[task] ', task._state)           # 打印任务状态
    # 给任务添加回调函数，任务完成后执行，注意回调函数的最后一个参数须为 future
    # functools.partial 创建偏函数作为 add_done_callback 方法的参数
    # 而 task 本身作为回调函数的最后一个参数
    task.add_done_callback(functools.partial(callback, 'coroutine'))
    loop.run_until_complete(task)           # 将任务注入事件循环并启动
    print('[task] ', task._state)           # 打印任务状态
    print('----- 运行耗时：{:.4f}s -----'.format(time.time()-start))

# 版本四
def four():
    start = time.time()
    async def do_some_work(t):
        print('[do_some_work]  这是个协程任务')
        # await 等同于 yield from
        # 只有由 asyncio.coroutine 装饰的函数内才可使用 yield from
        # 只有由 async 关键字定义的函数才可使用 await
        await asyncio.sleep(.1)              # 假装 IO 耗时 0.1 秒
        return '[do_some_work]  Coroutine four done'.format(t)
    coroutine = do_some_work('two')         # 创建协程
    loop = asyncio.get_event_loop()         # 创建事件循环
    task = loop.create_task(coroutine)      # 将协程作为参数创建任务
    print('[task] ', task._state)           # 打印任务状态
    loop.run_until_complete(task)           # 将任务注入事件循环并启动
    print('[task] ', task._state)           # 打印任务状态
    # 打印协程返回值，注意只有协程结束后才可获得返回值
    print(task.result())                    
    print('----- 运行耗时：{:.4f}s -----'.format(time.time()-start))
    
