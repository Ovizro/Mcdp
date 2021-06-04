"""
Prepare basic datapack dirs for Mcdp lancher.
"""

import os
import ujson
import asyncio
from shutil import copyfile
from functools import partial
from pathlib import PurePath
from typing import Any, Callable, Dict, Optional, Set, Union

from .context import get_context, Context, TagManager
from .version import get_version
from .aio_stream import Stream, mkdir, makedirs

async def init_mcmeta(desc: str, version: Union[int, str]) -> None:
    async with Stream("pack.mcmeta") as f:
        if isinstance(version, str):
            version = get_version(version)
        contain = {
            "pack":{
                "pack_format": version,
                "description": desc
            }
        }
        data = ujson.dumps(contain, indent=4)
        await f.awrite(data)

def init_name_space(name: str, *, used: Optional[Set[str]] = None) -> None:
    dirs = {
        "advancements", 
        "functions", 
        "loot_tables", 
        "predicates", 
        "structures", 
        "recipes", 
        "item_modifiers", 
        "dimension_type", 
        "dimension", 
        "worldgen"
    }
    for d in dirs:
        if used:
            if not d in used:
                continue
        path = os.path.join(name, d)
        os.makedirs(path, exist_ok=True)
    
    dirs = {
        "blocks",
        "entity_types",
        "items",
        "fluids",
        "functions"
    }
    tag_path = os.path.join(name, "tags")
    for d in dirs:
        path = os.path.join(tag_path, d)
        os.makedirs(path, exist_ok=True)

def analyse_file_struct(
    struct: Union[dict, str], 
    base: Optional[Union[os.PathLike, str]] = None
) -> Dict[str, Union[os.PathLike, str]]:

    if isinstance(struct, str):
        struct = ujson.loads(struct)
        
    ans = {}
    for k,v in struct.items():
        if not base:
            path = k
        else:
            path = os.path.join(base, k)
        
        if isinstance(v, str):
            ans[v] = path
        else:
            ans.update(analyse_file_struct(v, path))
    
    return ans
    
async def init_context() -> None:
    ...

async def build_dirs(
    name: str,
    description: str,
    version: Union[int, str] = 4,
    *,
    iron_path: Optional[Union[os.PathLike, str]] = None,
    namespace: Optional[str] = None
) -> None:
    """
    Build datapack.
    File struction:
        name
        |-- pack.mcmeta
        |-- pack.png
        |-- data
            |-- minecraft
            |   |-- tags
            |       |-- functions
            |           |-- tick.json
            |           |-- load.json
            |-- namespace
                |-- advancements
                |   |-- ...
                |-- functions
                |   |-- main.mcfunction
                |   |-- ...
                |-- loot_tables
                |-- predicates
                |-- ...
    """
    await mkdir(name)
    os.chdir(name)
    asyncio.ensure_future(init_mcmeta(description, version))
    
    if iron_path:
        copyiron = partial(copyfile, iron_path, "pack.png")
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, copyiron)
    
    await mkdir("data")
    os.chdir("data")
    namespace = namespace or name
    asyncio.ensure_future(mkdir("minecraft"))
    await mkdir(namespace)
    
    