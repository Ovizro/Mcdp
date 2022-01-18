import time
import warnings
from inspect import signature, Parameter
from typing import (Callable, Coroutine, Dict, List, Mapping, NoReturn,
                    Union, Optional, Any, Tuple, Type, overload)

from .counter import Counter, get_counter
from .typing import McdpVar, Variable
from .config import Config, get_config, MCFuncConfig
from .context import Context, Handler, TagManager, add_tag, insert, comment, newline
from .compiler import BaseCompilter, Function, FunctionHandler, lib_func, pull, push
from .command import AsInstruction, Selector
from .entities import McdpStack, get_tag
from .variable import Score, Scoreboard, dp_int, dp_score, global_var, init_global
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
        s = dp_score("mcfarg_{0}_{1}".format(name, k), init=False, simulation=ann, stack_id=-2,
                     display={"text": f"Mcdp function {name} arguments", "color": "dark_blue"})
        if v.KEYWORD_ONLY:
            kwds[k] = s
        else:
            args.append(s)
    return args, kwds

def _empty_function() -> NoReturn:
    raise NotImplementedError


class MCFunctionHandler(FunctionHandler):

    __slots__ = ["func"]

    def __init__(self, func: Callable) -> None:
        self.func = func
        super().__init__(func)
    
    def init(self) -> None:
        sig = signature(self.func)

        comment(f"Function '{self.func.__name__}'")
        newline()
        comment(f"Signature:\n{sig}")
        if self.func.__doc__:
            newline()
            comment("Doc:", self.func.__doc__)
        newline(2)
        

class MCFunction(Function):

    __slots__ = ["overload", "namespace", "overload_counter", "config"]
    __accessible__ = {"__name__": 1}

    def __new__(cls, name: str, **kwds) -> Any:
        if name in cls.collections:
            ins = cls.collections[name]
            return ins
        else:
            return McdpVar.__new__(cls)

    def __init__(self, name: str, *, space: Optional[str] = None, namespace: Optional[str] = None, config: MCFuncConfig = MCFuncConfig()) -> None:
        if '.' in name:
            name = name.split('.')[-1]
        super().__init__(_empty_function, space = space)
        self.namespace = namespace
        self.config = config
        self.overload: List[Callable] = []
        self.overload_counter: List[Counter] = []

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
        if self.overload:
            func.__name__ += str(len(self.overload))
        self.overload.append(func)

        if len(self.overload) > 1 and not self.config.allow_overload:
            raise RuntimeError("Config setting has forbidden function overload.")
        self.overload_counter.append(Counter(self.__name__))

    def set_config(self, **kwds) -> None:
        self.config = self.config.parse_obj(kwds)

    def apply(self) -> None:
        for i in range(len(self.overload)):
            f = self.overload[i]

            if not (len(self.overload) == 1 or self.overload_counter[i]):
                continue
                
            with Context(f.__name__, hdls=MCFunctionHandler(f)):
                for t in self.config.tag:
                    add_tag(t)

                sig = signature(f).parameters
                args, kwds = _get_arguments(self.__name__, sig)

                ans = f(*args, **kwds)
                if isinstance(ans, Score):
                    if ans.name != "dpc_return":
                        dp_score("dpc_return", ans, stack_id=-2,
                                display={"text": "Mcdp function return cache", "color": "dark_blue"})
                push()

    @classmethod
    def apply_all(cls) -> None:
        for i in cls.collections.values():
            i.apply()

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
                +self.overload_counter[i]
                break
        else:
            raise TypeError("Invalid arguments. No overloaded function signature is matched.")

        for k, v in binded.arguments.items():
            if issubclass(type(v), Score):
                dp_score("mcfarg_{0}_{1}".format(self.__name__, k), v,
                         display={"text": f"Mcdp function {self.__name__} arguments", "color": "dark_blue"})

        self.space = str(Context.get_relative_path())
        self.func = self.overload[i]

        pull()
        with AsInstruction(Selector("@e", "tag=stack_top", tag=get_tag())):
            super().__call__()
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


class Compiler(BaseCompilter):

    __slots__ = ["start_time"]

    def __init__(self, config: Optional[Config] = None) -> None:
        self.start_time = time.process_time_ns()
        super().__init__(config)
    
    @staticmethod
    def pull() -> None:
        enter_stack()
    



@overload
def mcfunc_main(func: Callable) -> None:
    ...
@overload
def mcfunc_main(*flags: str, **kw: Any) -> Callable[[Callable], None]:
    ...
def mcfunc_main(func: Optional[Union[Callable, str]] = None, *flags, **kw):
    def mf_main(func: Callable[[], Any], cfg: MCFuncConfig) -> None:
        #config = get_config()
        start = time.process_time_ns()
        with Context:
            add_tag("minecraft:load")
            init_global()

            with Context("__main__", hdls=Handler("__main__")):
                comment("This is the main function of the datapack.")
                newline(2)

                for t in cfg.tag:
                    add_tag(t)
                pull()
                func()
                push()

            with Context('__init_score__', hdls=Handler("__init_score__")):
                comment("Init the scoreborad.")
                newline(2)

                Scoreboard.apply_all()

            MCFunction.apply_all()
            TagManager.apply_all()
        
        end = time.process_time_ns()
        process = end - start
        process *= 1e-8
        print(f"Complite completed in {process} ms")
        get_counter().print_out()

    cfg = MCFuncConfig(**kw)

    if isinstance(func, str):
        flags += (func,)
    if not 'load' in flags and not 'tick' in flags:
        flags += ('load',)

    if callable(func):
        handle_flag(func, cfg, *flags)
        mf_main(func, cfg)
    else:
        def get_func(func: Callable[[], Coroutine]) -> None:
            handle_flag(func, cfg, *flags)
            mf_main(func, cfg)
        
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

mcdp_stack_id = global_var(dp_score, "mcdpStackID", 0)

@lib_func()
def enter_stack() -> None:
    global mcdp_stack_id

    top = Selector("@e", "tag=stack_top", tag=get_tag(), limit=1)
    lower = Selector("@e", "tag=lower_stack", tag=get_tag(), limit=1)
    
    lower.remove_tag("lower_stack")
    top.add_tag("lower_stack")
    top.remove_tag("stack_top")

    stack = McdpStack()
    mcdp_stack_id += 1
    

@lib_func()
def leave_stack() -> None:
    global mcdp_stack_id

    top = Selector("@e", "tag=stack_top", tag=get_tag(), limit=1)
    lower = Selector("@e", "tag=lower_stack", tag=get_tag(), limit=1)

    top.remove()
    lower.add_tag("stack_top")
    lower.remove_tag("lower_stack")

    mcdp_stack_id -= 2
    s = dp_score("mcdpStackID", selector=Selector(McdpStack))
    with s == mcdp_stack_id:
        Selector("@s").add_tag("lower_stack")
    mcdp_stack_id += 1
    

class McdpFunctionError(McdpError):
    ...