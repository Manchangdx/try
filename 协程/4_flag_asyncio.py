import asyncio
import aiohttp
import os, time, sys

# 20 个国家的 Country Code 列表
POP20CC = ('AA AC AG AJ AM AN AO AQ AR AS '
           'AU AX BA BB BF BH BG BK CH WZ').split()

# 创建保存图片的目录
if not os.path.isdir('flags_img'):
    os.makedirs('flags_img')
IMG_DIR = os.path.join(os.getcwd(), 'flags_img')

async def get_flag(cc):
    url_tmp = ('https://www.cia.gov/library/publications/'
        'the-world-factbook/attachments/flags/{}-flag.gif')
    async with aiohttp.ClientSession() as session:
        async with session.get(url_tmp.format(cc)) as resp:
            print('----------------------')
            print(await resp.text())
    async with aiohttp.request('GET', url_tmp.format(cc)) as r:
        resp = await r.text(encoding='UNICODE')
    image = await resp.read()
    return image

@asyncio.coroutine
def download_one(cc):
    image = yield from get_flag(cc)
    path = os.path.join(IMG_DIR, '{}.png'.format(cc))
    with open(path, 'wb') as f:
        f.write(response.content)
    print(cc, end=' ', flush=True)
    return cc

def main(cc_list):
    start_time = time.time()
    loop = asyncio.get_event_loop()
    tasks = [download_one(cc) for cc in cc_list]
    wait_coro = asyncio.wait(tasks)
    res, _ = loop.run_until_complete(wait_coro)
    end_time = time.time()
    print('\n下载 {} 个国旗，耗时 {:.2f} 秒。'.format(
        len(cc_list), end_time - start_time))

if __name__ == '__main__':
    main(POP20CC)
