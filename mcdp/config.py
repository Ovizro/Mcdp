from typing import Union
from pydantic import Field, validator
from .typings import McdpConfig, MinecraftVersionError

_dp_version_field = Field(default=6, const=True, ge=4)

def get_version(version: str) -> int:
    vlist = [int(v) for v in version.split(".")]

    if vlist[0] != 1 or vlist[1] < 13:
        raise MinecraftVersionError("only Minecraft version >= 1.13 can use datapack.")

    if vlist[1] == 13 or vlist[1] == 14:
        return 4
    elif vlist[1] == 15:
        return 5
    elif vlist[1] == 16:
        if len(vlist) <= 2:
            return 5
        if vlist[2] <= 1:
            return 5
        else:
            return 6
    elif vlist[1] == 17:
        return 7
    else:
        raise ValueError(f"unknow Minecraft datapack version {version}")

class Config(McdpConfig):
    package_name: str
    version: int = 6
    
    @validator("version")
    def _version(self, value: Union[str, _dp_version_field]) -> int:
        if isinstance(value, str):
            return get_version(value)
        else:
            return value