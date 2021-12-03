
times = 500

import cProfile

import aiofiles
import asyncio
import shutil
import random
import pyjion
import time
import os

pyjion.enable()

async_path = os.path.join('file_test', 'async')
with_path = os.path.join('file_test', 'with')

os.makedirs(async_path, exist_ok=True)
os.makedirs(with_path, exist_ok=True)

def with_file(info: str, t: int):
    with open(f'{with_path}/{t}.txt', 'w') as f:
        f.write(str(info))

async def async_file(info: str, t: int):
    async with aiofiles.open(f'{async_path}/{t}.txt', 'w') as f:
        await f.write(str(info))

async def aio_main():
    l = []
    for i in range(times):
        l.append(asyncio.ensure_future(async_file(random.randint(1, 100), i)))
    return l

def main():
    print(f'开始 {times} 次测试')
    start_time = time.perf_counter_ns()
    for i in range(times):
        with_file(random.randint(1, 100), i)
    end_time = time.perf_counter_ns()
    print(f'With: {end_time - start_time} ns')

    print('with 完成')
    
    l = asyncio.run(aio_main())
    start_time = time.perf_counter_ns()
    asyncio.gather(*l)
    end_time = time.perf_counter_ns()
    print(f'Async: {end_time - start_time} ns')

    print('async 完成')


cProfile.run('main()')
time.sleep(1)

shutil.rmtree(async_path)
shutil.rmtree(with_path)
