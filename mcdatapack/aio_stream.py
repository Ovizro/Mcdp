"""
High level interface for Mcdp lancher.
"""
import os
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

    __slots__ = ["opened", "write_tasks", "__file", "path"]

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
                if not os.path.isabs(root):
                    raise ValueError("param 'root' should be an absolute path.")
                if isinstance(root, PurePath):
                    path = root.joinpath(path)
                else:
                    path = os.path.join(root, path)

        if not isinstance(path, PurePath):
            self.path = PurePath(path)
        else:
            self.path: PurePath = path

    async def open(self) -> None:
        if not os.path.isdir(self.path.parent):
            await aio_makedirs(self.path.parent)
        self.__file = await aio_open(self.path, "w", encoding="utf-8")
        self.write_tasks: List[asyncio.Task] = []
        self.opened = True
    
    def write(self, data: str) -> asyncio.Task:
        if not self.opened:
            raise asyncio.InvalidStateError("I/O operation without open the file.")

        task = asyncio.create_task(self.__file.write(data))
        self.write_tasks.append(task)
        return task

    async def awrite(self, data: str) -> None:
        if not self.opened:
            raise asyncio.InvalidStateError("I/O operation without open the file.")

        await self.__file.write(data)

    async def close(self) -> int:
        ans = await asyncio.gather(*self.write_tasks)
        asyncio.create_task(self.__file.close())
        return sum(ans)
    
    def __await__(self):
        yield from self.open().__await__()
        return self

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *args):
        await self.close()

if __name__ == "__main__":
    s = Stream(PurePath("test/test.txt"))
    async def main():
        async with s:
            await s.write("hhh")
    asyncio.run(main())
