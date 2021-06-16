import warnings
from asyncio import iscoroutinefunction, run
from inspect import signature, Parameter
from typing import (Callable, Coroutine, Dict, List, Mapping,
    Union, Optional, Any, Tuple, Type, overload)

from .counter import Counter, get_counter
from .file_struct import build_dirs_from_config, init_context
from .typings import McdpVar, Variable
from .config import get_config, MCFuncConfig
from .context import Context, TagManager, add_tag, insert
from .variable import ScoreType, Scoreboard, dp_int, dp_score

def _toMcdpVar(c: Type) -> Type[McdpVar]:
    if c == int:
        return dp_int
    raise ValueError("Unsupported function argument type.")

def _get_arguments(name: str, param: Mapping[str, Parameter]) -> Tuple[list, dict]:
    args = []
    kwds = {}
    for k, v in param.items():
        ann = v.annotation
        if not issubclass(ann, McdpVar):
            ann = _toMcdpVar(ann)
        s = dp_score("mcfarg_{0}_{1}".format(name, k), init=False)
        if v.KEYWORD_ONLY:
            kwds[k] = s
        else:
            args.append(s)
    return args, kwds
    
class MCFunction(McdpVar):
    
    __slots__ = ["__name__", "overload", "namespace", "overload_counter", "config"]
    __accessible__ = ["__name__"]
    
    collection: Dict[str, "MCFunction"] = {}
    
    def __new__(cls, name: str, **kw) -> Any:
        if name in cls.collection:
            ins = cls.collection[name]
            if kw:
                ins.set_config(**kw)
            return ins
        else:
            return McdpVar.__new__(cls)
    
    def __init__(self, name: str, *, namespace: Optional[str] = None, **kw) -> None:
        if '.' in name:
            self.__name__ = name.split('.')[-1]
        else:
            self.__name__ = name
        self.namespace = namespace
        self.config = MCFuncConfig(**kw)
        self.overload: List = []
        self.overload_counter: List[Counter] = []
    
    def register(self, func: Callable) -> None:
        s = signature(func)
        sig = s.parameters
        if not (s.return_annotation is None or issubclass(s.return_annotation, McdpVar)):
            func.__annotations__['return'] = _toMcdpVar(s.return_annotation)
        for k in sig:
            ann = sig[k].annotation
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
                continue
            
            if i == 0:
                await Context.enter(self.__name__)
            else:
                await Context.enter(self.__name__+str(i))
            sig = signature(f).parameters
            args, kwds = _get_arguments(self.__name__, sig)
            
            ans = f(*args, **kwds)
            if isinstance(ans, ScoreType):
                dp_score("dpc_return", ans, stack_offset=1)
            Context.dynamic_pop()
            await Context.exit()
    
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
        
        for k,v in binded.arguments.items():
            if issubclass(type(v), ScoreType):
                dp_score("mcfarg_{0}_{1}".format(self.__name__, k), v)
            
        path = Context.get_relative_path() / self.__name__
        Context.dynamic_pull()
        self.namespace = self.namespace or get_config().namespace
        file = f"{self.namespace}:{path}"
        if ind != 0:
            insert(f"execute as @e[tag=stack_top] run function {file}{ind}")
        else:
            insert(f"execute as @e[tag=stack_top] run function {file}")
            
        T_ret = sig.return_annotation
        if not T_ret is None:
            ret = dp_score("dpc_return", init=False)
            if T_ret is dp_score:
                return ret
            else:
                return T_ret(ret)
        
@overload
def mcfunc(func: Callable) -> MCFunction:
    ...
@overload
def mcfunc(*args, **kw) -> Callable[[Callable], MCFunction]:
    ...
def mcfunc(func: Optional[Callable] = None, *args, **kw):
    def wrapper(_func: Callable) -> MCFunction:
        m = MCFunction(func.__qualname__, **kw)
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
def mcfunc_main(*args, **kw) -> Callable[[Callable], None]:
    ...
def mcfunc_main(func: Optional[Union[Callable]] = None, *args, **kw):
    async def md_main(func: Callable[[], Optional[Coroutine]]) -> None:
        config = get_config()
        await build_dirs_from_config()
        context = init_context(config.namespace)
        async with context:
            if iscoroutinefunction(func):
                await func()
            else:
                func()
            add_tag('load', namespace='minecraft')
            
            await MCFunction.apply_all()
            TagManager.apply_all()
            
            await context.enter('__init_score__')
            Scoreboard.apply_all()
            await context.exit()
            
        get_counter().print_out()
    
    if callable(func):
        run(md_main(func))
    else:
        def get_func(func: Callable[[], Optional[Coroutine]]) -> None:
            run(md_main(func))
        return get_func
            