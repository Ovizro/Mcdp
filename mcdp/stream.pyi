from typing import Any, Final, Literal, Optional


def mkdir(dir_path: str) -> None: ...

class Stream:
    path: Final[str]

    def __init__(self, path: str, *, root: Optional[str] = None) -> None: ...
    def open(self, mod: Literal['w', 'a'] = 'w') -> None: ...
    def fwrite(self, _s: bytes) -> int: ...
    def write(self, _s: str) -> int: ...
    def dump(self, data: Any) -> int: ...
    def close(self) -> None: ...
    def writable(self) -> bool: ...
    @property
    def closed(self) -> bool: ...
    def __enter__(self) -> "Stream": ...
    def __exit__(self, exc_type, exc_ins, traceback) -> None: ...