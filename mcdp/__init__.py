from typing import Optional

from .config import Config, PackageImformation, get_config, T_version, set_config

from .version import __version__
from .stream import Stream


__author__ = "Ovizro"
__author_email__ = "Ovizro@hypercol.com"
__maintainer__ = ["Tatersic", "ExDragine"]
__maintainer_email__ = ["Tatersic@qq.com", "ExDragine@hypercol.com"]


class Mcdatapack:
    __slots__ = ["config", ]

    def __init__(
            self,
            name: str,
            version: T_version,
            description: str,
            *,
            namespace: Optional[str] = None,
            icon_path: Optional[str] = None,
            **kw
    ) -> None:
        namespace = namespace or name
        pack = PackageImformation(name=name, support_version=version, description=description,
                namespace=namespace, icon_path=icon_path)
        self.config = Config(package = pack, **kw)
        set_config(self.config)

__all__ = [
    "Mcdatapack",
    # config
    "Config",
    "config",
    "get_config",
]
