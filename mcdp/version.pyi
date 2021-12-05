from typing import Any, Dict, List, NoReturn, Tuple, Callable, Union, Optional, TypeVar, overload


T_version = Union[Tuple[int, ...], str, "Version"]
TS_version = Union[Tuple[Union[str, int], ...], str, "PhaseVersion"]


class Version:
    """
    The base class in model 'version'.
    Support boolean operations between version numbers like '1.0.2'.
    """

    def __init__(self, version: T_version) -> None:...
    @overload
    def __getitem__(self, key: int) -> int:
        ...
    @overload
    def __getitem__(self, key: slice) -> Tuple[int, ...]:
        ...
    def __getitem__(self, key: Union[int, slice]) -> Union[int, Tuple[int, ...]]:...
    def __iter__(self) -> Tuple[int, ...]:...
    @classmethod
    def __get_validators__(cls):...
    @classmethod
    def validate(cls, val: Union[str, "Version"]):...
    def __eq__(self, other: T_version) -> bool:...
    def __ne__(self, other: T_version) -> bool:...
    def __gt__(self, other: T_version) -> bool:...
    def __ge__(self, other: T_version) -> bool:...
    def __lt__(self, other: T_version) -> bool:...
    def __le__(self, other: T_version) -> bool:...
    def __len__(self) -> int:...
    @overload
    def get_number(self, *, extend: Optional[int] = None) -> Tuple[int, ...]:
        ...
    @overload
    def get_number(self, index: int , *, extend: Optional[int] = None) -> int:
        ...
    def get_number(self, index: Optional[int] = None, *, extend: Optional[int] = None) -> Union[Tuple[int, ...], int]:...
    def check(self,
        *args: str,
        eq: Union[List[T_version], T_version] = [],
        ne: Union[List[T_version], T_version] = [],
        gt: Optional[T_version] = None,
        ge: Optional[T_version] = None,
        lt: Optional[T_version] = None,
        le: Optional[T_version] = None
    ) -> Callable[[Callable], Callable]:...
    def __repr__(self) -> str:...
    def __str__(self) -> str:...


class PhaseVersion(Version):
    """
    Just add a version phase like 'Alpha' or 'Beta'. 
    (In fact, 'Python 3.8.3' is valid, too.)
    
    The phase mark only used in '==' and '!=' when both sides have a phase mark.
    That is to say:
        ```
        v = PhaseVersion('Beta 1.5.2')
        v == '1.5.2'        #True
        v == 'Alpha 1.5.2'  #False
        v >= 'Alpha 1.4'    #True
        ```
    """

    def __init__(self, version: T_version, *, phase: Optional[str] = None) -> None:...

__version__: PhaseVersion

def fail_version_check(func: Callable, *, collection: Dict[str, Callable] = ...) -> Callable:...
def pass_version_check(func: Callable, *, collection: Dict[str, Callable] = ...) -> Callable:...
def analyse_check_sentences(
        *args: str,
        eq: Union[List[T_version], T_version] = [],
        ne: Union[List[T_version], T_version] = [],
        gt: Optional[T_version] = None,
        ge: Optional[T_version] = None,
        lt: Optional[T_version] = None,
        le: Optional[T_version] = None
) -> Dict[str, Union[List[T_version], T_version, None]]:...
def version_check(
        version: Version,
        *args: str,
        eq: Union[List[T_version], T_version] = [],
        ne: Union[List[T_version], T_version] = [],
        gt: Optional[T_version] = None,
        ge: Optional[T_version] = None,
        lt: Optional[T_version] = None,
        le: Optional[T_version] = None
) -> Callable[[Callable], Callable]:
    """
    The core function of the version check.
    """

class VersionChecker:
    """
    The helper of version checker.
    
    Sometimes the version cannot be fetched when inited, so class VersionChecker is created.
    The final function will be insure when the function is first called.
    
    In the same time, the class supports the multiple version check.
    """

    def __init__(self, version_factory: Callable[[], Version]) -> None:...
    def register(self, func: Callable, *args: str, **kwds) -> None:...
    
    @property
    def decorator(self) -> Callable[..., Callable[[Callable], Callable]]:...
    def apply_check(self) -> None:...
    def __call__(self, *args: Any, **kwds: Any) -> Any:...


class AioCompatVersionChecker(VersionChecker):
    """
    The async compat version of class VersionCheck.
    """
    @property
    def decorator(self) -> Callable[..., Callable[[Callable], Callable]]:...
    async def __call__(self, *args: Any, **kwds: Any) -> Any:...

class VersionError(Exception):
    def __init__(self, *msg, version: Optional[Version] = None) -> None:...