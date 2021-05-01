"""
High level interface for Mcdp lancher.
"""
import os
import asyncio
from aiofile import AIOFile
from typing import List, Optional, Union, Any, IO

def file_open(path: os.PathLike, mode: str = 'w', **kw) -> IO[Any]:
    """
    Open a file whether or not the dir exists.
    """
    if not os.path.isfile(path):
        p = os.path.split(path)
        if not os.path.isdir(p[0]) and p[0]:
            os.makedirs(p[0])
    return open(path, mode, **kw)
    
async def waitTask(*tasks: Union[asyncio.Task, asyncio.Future]) -> None:
    for task in tasks:
        if not task.done():
            ans.append(await task)

class Stream(AIOFile):

    __slots__ = ["opened", "write_tasks"]

    async def open(self) -> Optional[int]:
        fileno = await super().open()
        self.write_tasks: List[asyncio.Task] = []
        self.opened = True
        return fileno
    
    def write(self, data: str, *, offset: int = 0) -> None:
        if not self.opened:
            raise asyncio.InvalidStateError("I/O operation without open the file.")

        task = asyncio.create_task(super().write(data, offset=offset))
        self.write_tasks.append(task)

    async def awrite(self, data: str, *, offset: int = 0) -> None:
        if not self.opened:
            raise asyncio.InvalidStateError("I/O operation without open the file.")

        await super().write(data, offset=offset)

    async def close(self) -> None:
        await waitTask(*self.write_tasks)
        asyncio.create_task(super().close())