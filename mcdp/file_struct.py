"""
Prepare basic datapack dirs for Mcdp lancher.
"""

import os
import asyncio
import ujson
from functools import partial
from pathlib import Path, PurePath
from typing import Any, Callable, Dict, Optional, Set, Union

from .context import Context, Context, TagManager
from .config import get_version, get_config, T_version
from .aio_stream import Stream, mkdir, makedirs, rmtree, copyfile


async def init_mcmeta(desc: str, version: T_version) -> None:
    async with Stream(os.path.abspath("pack.mcmeta")) as f:
        if not isinstance(version, int):
            version = get_version(version)
        contain = {
            "pack": {
                "pack_format": version,
                "description": desc
            }
        }
        await f.adump(contain)


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
    for k, v in struct.items():
        if not base:
            path = k
        else:
            path = os.path.join(base, k)

        if isinstance(v, str):
            ans[v] = path
        else:
            ans.update(analyse_file_struct(v, path))

    return ans


async def build_dirs(
        name: str,
        version: T_version,
        description: str,
        *,
        iron_path: Optional[Union[os.PathLike, str]] = None,
        namespace: Optional[str] = None,
        remove_old_pack: bool = True
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
    if remove_old_pack and Path(name).is_dir():
        await rmtree(f'{name}/data')
    else:
        await mkdir(name)
    os.chdir(name)
    all_tasks = []
    all_tasks.append(asyncio.ensure_future(init_mcmeta(description, version)))

    if iron_path:
        all_tasks.append(asyncio.ensure_future(copyfile(iron_path, "pack.png")))

    await mkdir("data")
    os.chdir("data")
    namespace = namespace or name
    all_tasks.append(asyncio.ensure_future(mkdir("minecraft")))
    await mkdir(namespace)

    await asyncio.gather(*all_tasks)
    Context.init(namespace)


async def build_dirs_from_config() -> None:
    cfg = get_config()
    await build_dirs(
            cfg.name,
            cfg.version,
            cfg.description,
            iron_path=cfg.iron_path,
            namespace=cfg.namespace,
            remove_old_pack=cfg.remove_old_pack
    )
