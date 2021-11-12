import warnings
from asyncio import iscoroutinefunction, run
from inspect import signature, Parameter
from typing import (Callable, Coroutine, Dict, List, Mapping, NoReturn,
                    Union, Optional, Any, Tuple, Type, overload)

from .counter import Counter, get_counter
from .file_struct import build_dirs_from_config
from .typings import McdpVar, Variable
from .config import get_config, get_version, MCFuncConfig
from .context import Context, TagManager, add_tag, insert, comment, newline, get_namespace
from .variable import Score, Scoreboard, dp_int, dp_score
from .exceptions import *


def _toMcdpVar(c: Type) -> Type[Variable]:
    if c == int:
        return dp_int
    raise McdpValueError("Unsupported function argument type.")


def _get_arguments(name: str, param: Mapping[str, Parameter]) -> Tuple[list, dict]:
    args = []
    kwds = {}
    for k, v in param.items():
        ann = v.annotation
        if not issubclass(ann, Variable):
            ann = _toMcdpVar(ann)
        s = dp_score("mcfarg_{0}_{1}".format(name, k), init=False, simulation=ann, stack_offset=1,
                     display={"text": f"Mcdp function {name} arguments", "color": "dark_blue"})
        if v.KEYWORD_ONLY:
            kwds[k] = s
        else:
            args.append(s)
    return args, kwds


def add_comment(func: Callable) -> None:
    sig = signature(func)
    comment(f"Function '{func.__name__}'", f"\nSignature:\n{sig}")
    if func.__doc__:
        comment("\nDoc:", func.__doc__)
    newline(2)


class MCFunction(McdpVar):

    __slots__ = ["__name__", "overload", "namespace", "overload_counter", "config"]
    __accessible__ = ["__name__"]

    collection: Dict[str, "MCFunction"] = {}

    def __new__(cls, name: str, **kwds) -> Any:
        if name in cls.collection:
            ins = cls.collection[name]
            return ins
        else:
            return McdpVar.__new__(cls)

    def __init__(self, name: str, *, namespace: Optional[str] = None, config: MCFuncConfig = MCFuncConfig()) -> None:
        if '.' in name:
            self.__name__ = name.split('.')[-1]
        else:
            self.__name__ = name
        self.namespace = namespace
        self.config = config
        self.overload: List = []
        self.overload_counter: List[Counter] = []
        self.__class__.collection[name] = self

    def register(self, func: Callable) -> None:
        s = signature(func)
        sig = s.parameters
        if not (s.return_annotation is None or issubclass(s.return_annotation, Variable)):
            func.__annotations__['return'] = _toMcdpVar(s.return_annotation)
        for k in sig:
            ann = sig[k].annotation
            if not issubclass(ann, Variable):
                func.__annotations__[k] = _toMcdpVar(ann)
                warnings.warn("Argument annotations of the mcfunction should be a subclass of Varible.",
                              SyntaxWarning)
            if not ann:
                raise SyntaxError("Miss mcfunction arguments type annotation.")
        if not func.__name__ == self.__name__:
            warnings.warn(
                    f"unsuit function name. Maybe you are deliberate?", RuntimeWarning)
        self.overload.append(func)

        if len(self.overload) > 1 and not self.config.allow_overload:
            raise RuntimeError("Config setting has forbidden function overload.")
        self.overload_counter.append(Counter(self.__name__))

    def set_config(self, **kwds) -> None:
        self.config = self.config.parse_obj(kwds)

    async def apply(self) -> None:
        for i in range(len(self.overload)):
            f = self.overload[i]

            if not (len(self.overload) == 1 or self.overload_counter[i]):
                print(Context.get_relative_path())
                continue

            if i == 0:
                name = self.__name__
            else:
                name = self.__name__ + str(i)
                
            async with Context(name):
                for t in self.config.tag:
                    add_tag(t)

                if get_config().pydp.add_function_comments:
                    add_comment(f)

                sig = signature(f).parameters
                args, kwds = _get_arguments(self.__name__, sig)

                ans = f(*args, **kwds)
                if isinstance(ans, Score):
                    if ans.name != "dpc_return":
                        dp_score("dpc_return", ans, stack_offset=1,
                                display={"text": "Mcdp function return cache", "color": "dark_blue"})
                Context.leave()

    @classmethod
    async def apply_all(cls) -> None:
        for i in cls.collection.values():
            await i.apply()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        for i in range(len(self.overload)):
            func = self.overload[i]
            sig = signature(func)
            try:
                binded = sig.bind(*args, **kwds)
                binded.apply_defaults()
                for k in sig.parameters:
                    if not isinstance(binded.arguments[k], sig.parameters[k].annotation):
                        raise TypeError
            except:
                continue
            else:
                ind = i
                +self.overload_counter[i]
                break
        else:
            raise TypeError("Invalid arguments. No overloaded function signature is matched.")

        for k, v in binded.arguments.items():
            if issubclass(type(v), Score):
                dp_score("mcfarg_{0}_{1}".format(self.__name__, k), v,
                         display={"text": f"Mcdp function {self.__name__} arguments", "color": "dark_blue"})

        path = Context.get_relative_path() / self.__name__
        Context.enter()
        self.namespace = self.namespace or get_config().namespace
        file = f"{self.namespace}:{path}"
        if ind != 0:
            insert(f"execute as @e[tag=stack_top] run function {file}{ind}")
        else:
            insert(f"execute as @e[tag=stack_top] run function {file}")

        T_ret = sig.return_annotation
        if not T_ret is None:
            return dp_score("dpc_return", init=False, simulation=T_ret,
                            display={"text": f"Mcdp function return cache", "color": "dark_blue"})


@overload
def mcfunc(func: Callable) -> MCFunction:
    ...
@overload
def mcfunc(*flags: str, **config: Any) -> Callable[[Callable], MCFunction]:
    ...
def mcfunc(func: Optional[Union[Callable, str]] = None, *flags: str, **config: Any):
    if isinstance(func, str):
        flags += (func,)

    def wrapper(_func: Callable) -> MCFunction:
        cfg = MCFuncConfig(**config)
        handle_flag(_func, cfg, *flags)
        m = MCFunction(_func.__qualname__, config=cfg)
        m.register(_func)
        return m

    if callable(func):
        return wrapper(func)
    else:
        return wrapper


@overload
def mcfunc_main(func: Callable) -> None:
    ...
@overload
def mcfunc_main(*flags: str, **kw: Any) -> Callable[[Callable], None]:
    ...
def mcfunc_main(func: Optional[Union[Callable, str]] = None, *flags, **kw):
    async def mf_main(func: Callable[[], Any], cfg: MCFuncConfig) -> None:
        config = get_config()
        await build_dirs_from_config()
        async with Context:
            add_tag("minecraft:load")
            comment(
                f"Datapack {config.name} built by Mcdp.",
                "",
                f"Supported Minecraft version: {config.version} ({get_version(config.version)})",
                "",
                "This is the initize function."
            )
            newline(2)

            async with Context("__main__"):
                for t in cfg.tag:
                    add_tag(t)
                if iscoroutinefunction(func):
                    await func()
                else:
                    func()

            async with Context('__init_score__'):
                Scoreboard.apply_all()

            await MCFunction.apply_all()
            await TagManager.apply_all()
            
        get_counter().print_out()

    cfg = MCFuncConfig(**kw)

    if isinstance(func, str):
        flags += (func,)
    if not 'load' in flags and not 'tick' in flags:
        flags += ('load',)

    if callable(func):
        handle_flag(func, cfg, *flags)
        run(mf_main(func, cfg))
    else:
        def get_func(func: Callable[[], Coroutine]) -> None:
            handle_flag(func, cfg, *flags)
            run(mf_main(func, cfg))
        
        return get_func

T_FlagHandler = Callable[[Callable, MCFuncConfig], None]
_func_flag_handlers: Dict[str, T_FlagHandler] = {}

def mcfunc_frag(flag: str) -> Callable[[T_FlagHandler], T_FlagHandler]:
    def get_flag_handler(func: T_FlagHandler) -> T_FlagHandler:
        _func_flag_handlers[flag] = func
        return func
    return get_flag_handler

def handle_flag(func: Callable, cfg: MCFuncConfig, *flag: str) -> None:
    for f in flag:
        if not f in _func_flag_handlers:
            raise McdpFunctionError(f"Invalid function flag {f}")
        _func_flag_handlers[f](func, cfg)

@mcfunc_frag("load")
def _flag_load(func: Callable, cfg: MCFuncConfig) -> None:
    cfg.tag.add("minecraft:load")

@mcfunc_frag("tick")
def _flag_tick(func: Callable, cfg: MCFuncConfig) -> None:
    cfg.tag.add("minecraft:tick")

class McdpFunctionError(McdpError):
    ...