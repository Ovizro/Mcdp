"""
High level interface for Mcdp lancher.
"""
import os
import ujson
import asyncio
from pathlib import PurePath
from functools import partial, wraps
from typing import IO, Any, List, Optional, Union

from aiofiles import open as aio_open

def aio_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run

aio_makedirs = aio_wrap(os.makedirs)
    
class Stream:

    __slots__ = ["opened", "closed", "write_tasks", "__file", "path"]

    pathtools = os.path

    def __init__(
    	self,
    	path: Union[str, os.PathLike],
    	*,
    	root: Optional[Union[str, os.PathLike]] = None
    ) -> None:
        
        if not os.path.isabs(path):
            if not root:
                path = os.path.abspath(path)
            else:
                if isinstance(root, PurePath):
                    path = root.joinpath(path)
                else:
                    path = os.path.join(root, path)

        if not isinstance(path, PurePath):
            self.path = PurePath(path)
        else:
            self.path: PurePath = path
            
        self.opened = False
        self.closed = False

    async def open(self) -> None:
        if self.opened:
            return
        if not os.path.isdir(self.path.parent):
            await aio_makedirs(self.path.parent)
        self.__file = await aio_open(self.path, "w", encoding="utf-8")
        self.write_tasks: List[asyncio.Task] = []
        self.opened = True
        self.closed = False
    
    def write(self, data: str) -> asyncio.Task:
        self._check()
        task = asyncio.create_task(self.__file.write(data))
        self.write_tasks.append(task)
        return task
        
    def dump(self, data: dict) -> None:
        string = ujson.dumps(data)
        self.write(string)

    async def awrite(self, data: str) -> None:
        self._check()
        await self.__file.write(data)
    
    async def flush(self) -> int:
        self._check()
        ans = await asyncio.gather(*self.write_tasks)
        await self.__file.flush()
        return sum(ans)
    
    async def close(self) -> int:
        if not self.opened:
            return
        ans = await asyncio.gather(*self.write_tasks)
        self.opened = False
        asyncio.create_task(self.__file.close())
        self.closed = True
        return sum(ans)
    
    def __await__(self):
        yield from self.open().__await__()
        return self

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *args):
        await self.close()
        
    def _check(self) -> None:
        if self.opened:
            return
        if self.closed:
            raise OSError("I/O operation on closed file.")
        else:
            raise OSError("I/O operation without opening the file.")

if __name__ == "__main__":
    s = Stream(PurePath("test/test.txt"))
    async def main():
        async with s:
            await s.write("hhh")
    asyncio.run(main())
