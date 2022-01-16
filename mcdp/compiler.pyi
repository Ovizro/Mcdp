from typing import Callable, Final, NoReturn, Optional

from .typing import McdpVar
from .config import Config
from .context import Context, Handler


class FunctionHandler(Handler):
    __func__: Final[Callable[[], None]]

    def __init__(self, func: Callable[[], None]) -> None: ...
    def init(self) -> None: ...


class Function(McdpVar):
    __func__: Final[Callable[[], None]]
    __name__: Final[str]

    def __init__(self, func: Callable[[], None], *, space: str) -> None: ...
    def __call__(self, namespace: Optional[str] = None) -> None: ...
    def apply(self, create_frame: bool = False) -> None: ...
    @staticmethod
    def apply_all(create_frame: bool = False) -> None: ...


class BaseCompilter:
    config: Final[Config]

    def __init__(self, config: Optional[Config] = None) -> None: ...
    def build_dirs(self) -> None: ...
    @staticmethod
    def pull() -> NoReturn: ...
    @staticmethod
    def push() -> NoReturn: ...
    def __enter__(self) -> "BaseCompilter": ...
    def __exit__(self, exc_type, exc_ins, traceback) -> None: ...


def lib_func(space: Optional[str] = "Libs") -> Callable[[Callable[[], None]], Function]: ...

@lib_func(None)
def __init_score__() -> NoReturn:
    raise NotImplementedError