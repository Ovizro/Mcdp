"""
Support async file stream for the Context.
"""
import os
import ujson
import asyncio
from pathlib import PurePath
from functools import partial, wraps
from aiofiles import open as aio_open
from typing import List, Optional, Union, TypeVar

from .counter import get_counter
counter = get_counter()

PathType = TypeVar("PathType", str, os.PathLike)

def aio_future(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run

@aio_future
def mkdir(path: PathType, *, exist_ok: bool = True) -> None:
    if os.path.isdir(path) and exist_ok:
        return
    os.mkdir(path)
    +counter.dirs

@aio_future
def makedirs(path: PathType, *, exist_ok: bool = True) -> None:
    if not os.path.isdir(path):
        test_path = PurePath(path).parent
        +counter.dirs
        while not os.path.isdir(test_path):
            +counter.dirs
            test_path_p = test_path.parent
            if test_path_p == test_path:
                break
            else:
                test_path = test_path_p
    elif exist_ok:
        return
    os.makedirs(path, exist_ok=exist_ok)
    
class Stream:

    __slots__ = ["opened", "closed", "write_tasks", "__file", "path"]

    pathtools = os.path

    def __init__(
    	self,
    	path: PathType,
    	*,
    	root: Optional[PathType] = None
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
        await makedirs(self.path.parent)
        self.__file = await aio_open(self.path, "w", encoding="utf-8")
        +counter.files
        
        self.write_tasks: List[asyncio.Task] = []
        self.opened = True
        self.closed = False
    
    def write(self, data: str) -> asyncio.Task:
        self._check()
        task = asyncio.ensure_future(self.__file.write(data))
        self.write_tasks.append(task)
        return task
        
    def dump(self, data: dict) -> None:
        string = ujson.dumps(data, indent=4)
        self.write(string)

    async def awrite(self, data: str) -> None:
        self._check()
        await self.__file.write(data)
    
    async def adump(self, data: dict) -> None:
        string = ujson.dumps(data)
        await self.awrite(string)
    
    def writable(self) -> bool:
        return self.opened and not self.closed
    
    async def flush(self) -> int:
        self._check()
        ans = await asyncio.gather(*self.write_tasks)
        await self.__file.flush()
        return sum(ans)
    
    async def close(self) -> int:
        if not self.opened:
            return 0
        ans = await asyncio.gather(*self.write_tasks)
        self.opened = False
        asyncio.ensure_future(self.__file.close())
        self.closed = True
        
        ans =  sum(ans)
        counter.chars += ans
        return ans
    
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
