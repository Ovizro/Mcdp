from asyncio.coroutines import iscoroutinefunction
from functools import partial
from warnings import warn
from io import StringIO
from typing import Any, Callable, Coroutine, Dict, List, Literal, Optional, Set, Tuple, Type, Union

from .config import get_config
from .typings import McdpBaseModel, McdpVar, McdpError
from .mcstring import MCString
from .context import Context, McdpContextError, comment, insert, ContextEnv, newline
from .exceptions import *


class PosComponent(McdpVar):

    __slots__ = ["type", "value"]

    def __init__(
            self,
            value: str,
            type: Optional[Literal["absolute", "relative", "local"]] = None
        ) -> None:
        self.value = value
        if '^' in value:
            if len(value) > 1:
                int(value[1:])
            self.type = "local"
        elif '~' in value:
            if len(value) > 1:
                int(value[1:])
            self.type = "relative"
        else:
            int(value)
            self.type = "absolute"
        if type and (type != self.type):
            raise McdpValueError("unsuit position value.")

    def __str__(self) -> str:
        return self.value

    __repr__ = __str__


class Position(McdpVar):

    __slots__ = ["_posXYZ", "type"]

    def __init__(self, pos: str) -> None:
        l = [PosComponent(i) for i in pos.split()]
        if len(l) != 3:
            raise McdpValueError("Incorrect position length.")

        tid = 0
        for i in l:
            if i.type == "absolute":
                if tid == 3:
                    raise McdpTypeError("Invalid position.")
                tid = 1
            elif i.type == "relative":
                if tid == 3:
                    raise McdpTypeError("Invalid position.")
                tid = 2
            else:
                if tid < 3 and tid != 0:
                    raise McdpTypeError("Invalid position.")
                tid = 3

        self._posXYZ = tuple(l)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Union[str, "Position"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)

    def __repr__(self) -> str:
        return f"Position{self._posXYZ}"

    def __str__(self) -> str:
        return " ".join([i.value for i in self._posXYZ])


class KeywordArg(McdpVar):

    __slots__ = ["name", "value"]

    def __new__(cls, name: Union[str, Dict[str, Any]], value: Union[str, Set["KeywordArg"], None] = None):
        if not value:
            ans = []
            for t in name.items():
                ans.append(cls(t[0], t[1]))
            return ans
        else:
            return McdpVar.__new__(cls)

    def __init__(self, name: str, value: Union[str, Set["KeywordArg"]]) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.value})"

    def __str__(self) -> str:
        if isinstance(self.value, set):
            value = '{' + ','.join((str(i) for i in self.value)) + '}'
        else:
            value = self.value
        return "{0}={1}".format(self.name, value)


class Selector(McdpBaseModel):
    name: Literal["@p", "@a", "@r", "@e", "@s"]
    args: List[Union[KeywordArg, str]] = []

    def __new__(cls, name_or_entity: Any, *args, **kwds):
        if not isinstance(name_or_entity, str):
            return name_or_entity.__selector__()
        return McdpBaseModel.__new__(cls)

    def __init__(self, name: Union[str, Any], *args, **kwds) -> None:
        if not isinstance(name, str):
            return
        if name in ["@p", "@a", "@r", "@e", "@s"]:
            l = list(args)
            l.extend(KeywordArg(kwds))
            super().__init__(name=name, args=l)
        else:
            _name = name[:2]
            _args = name[2:-1].split(',')
            _args.extend(args)

            super().__init__(name=_name, args=_args)
    
    def add_tag(self, tag: str) -> None:
        insert(f"tag {self} add {tag}")

    def remove_tag(self, tag: str) -> None:
        insert(f"tag {self} remove {tag}")
    
    def remove(self) -> None:
        insert(f"kill {self}")
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Any):
        if isinstance(val, cls):
            return val
        else:
            return val.__selector__()

    def __mcstr__(self) -> MCString:
        return MCString(selector=str(self))

    def __str__(self) -> str:
        if not self.args:
            return f"{self.name}"
        else:
            value = ','.join((str(i) for i in self.args))
            return f"{self.name}[{value}]"

    __repr__ = __str__


class NBTPath(McdpVar):

    __slots__ = ["path"]

    def __init__(self, *args: str) -> None:
        self.path = list(args)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Union[str, "NBTPath"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)

    def __repr__(self) -> str:
        return f"NBTPath({self.__str__()})"

    def __str__(self) -> str:
        return '.'.join(self.path)


class ContextInstructionEnv(ContextEnv):

    __slots__ = ["instruction", "decorate"]

    def __init__(self, instruction: "Instruction", *, decorate: bool = True) -> None:
        self.instruction = instruction
        self.decorate = decorate
        super().__init__(instruction.__class__.__name__)
    
    def init(self) -> None:
        super().init()
        comment(f"{repr(self.instruction.__class__.__name__)} file.")
        newline(2)
    
    def decorate_command(self, cmd: str) -> str:
        if not self.decorate:
            return cmd
        exec = Execute(self.instruction)
        return exec.command_prefix() + cmd


class Instruction(McdpBaseModel):

    stream: Optional[Context] = None

    def __init__(self) -> None:
        raise NotImplementedError

    def __bool__(self) -> Any:
        return NotImplemented
    
    def __enter__(self) -> "Instruction":
        env = ContextInstructionEnv(self)
        Context.add_env(env)
        return self
    
    def __exit__(self, exc_type, exc_ins, traceback) -> None:
        Context.pop_env()
    
    async def __aenter__(self) -> "Instruction":
        env = ContextInstructionEnv(self, decorate=False)
        self.stream = env.creat_stream()
        await self.stream.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_ins, traceback) -> None:
        if not self.stream:
            raise McdpContextError("No context provide.")
        await self.stream.__aexit__(exc_type, exc_ins, traceback)

    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"


class AlignInstruction(Instruction):
    axes: str

    def __init__(self, axes: str) -> None:
        x = axes.count('x')
        y = axes.count('y')
        z = axes.count('z')
        if x > 1 or y > 1 or z > 1 or x + y + z != len(axes):
            raise McdpValueError(
                    "Axes should be any non-repeating combination of the characters 'x', 'y', and 'z'.")
        McdpBaseModel.__init__(self, axes=axes)

    def __str__(self) -> str:
        return f"align {self.axes}"


class AnchoredInstruction(Instruction):
    anchor: Literal["eyes", "feet"]

    def __init__(self, anchor: Literal["eyes", "feet"]) -> None:
        McdpBaseModel.__init__(self, anchor=anchor)

    def __str__(self) -> str:
        return f"anchored {self.anchor}"


class AsInstruction(Instruction):
    targets: Union[Selector, str]

    def __init__(self, targets: Union[Selector, str]) -> None:
        McdpBaseModel.__init__(self, targets=targets)

    def __str__(self) -> str:
        return f"as {self.targets}"


class AtInstruction(Instruction):
    targets: Union[Selector, str]

    def __init__(self, targets: Union[Selector, str]) -> None:
        McdpBaseModel.__init__(self, targets=targets)

    def __str__(self) -> str:
        return f"at {self.targets}"


class FacingInstruction(Instruction):
    entity: bool
    pos: Optional[Position] = None
    targets: Optional[Selector] = None
    anchor: Literal["eyes", "feet"]

    def __init__(
            self,
            pos_or_targets: Union[str, Position, Selector],
            anchor: Optional[Literal["eyes", "feet"]] = None,
            *,
            entity: bool = False
    ) -> None:
        if entity:
            if not anchor:
                raise McdpValueError("Miss a argument 'anchor'.'")
            McdpBaseModel.__init__(
                    self, targets=pos_or_targets, anchor=anchor, entity=True)
        else:
            if anchor:
                raise McdpValueError("Invalid argument 'anchor'.")
            McdpBaseModel.__init__(self, pos=pos_or_targets, entity=entity)

    def __str__(self) -> str:
        if self.entity:
            return f"facing entity {self.targets} {self.anchor}"
        else:
            return f"facing {self.pos}"


class InInstruction(Instruction):
    dimension: str

    def __init__(self, dimension: str) -> None:
        McdpBaseModel.__init__(self, dimension=dimension)

    def __str__(self) -> str:
        return f"in {self.dimension}"


class PositionedInstruction(Instruction):
    entity: bool
    pos: Optional[Position] = None
    targets: Union[str, Selector, None] = None

    def __init__(self, pos_or_targets: Union[str, Position, Selector], *, entity: bool = False) -> None:
        if entity:
            McdpBaseModel.__init__(self, targets=pos_or_targets, entity=True)
        else:
            McdpBaseModel.__init__(self, pos=pos_or_targets, entity=False)

    def __str__(self) -> str:
        if self.entity:
            return f"positioned as {self.targets}"
        else:
            return f"positioned {self.pos}"


class RotatedInstruction(Instruction):
    entity: bool
    rot: Optional[Tuple[Union[int, float], Union[int, float]]] = None
    targets: Union[str, Selector, None] = None

    def __init__(self, rot_or_targets: Union[Tuple, str, Selector], *, entity: bool = False) -> None:
        if entity:
            McdpBaseModel.__init__(self, targets=rot_or_targets, entity=True)
        else:
            McdpBaseModel.__init__(self, rot=rot_or_targets, entity=entity)

    def __str__(self) -> str:
        if self.entity and self.targets:
            return f"rotated as {self.targets}"
        elif self.rot:
            return f"rotated {self.rot[0]} {self.rot[1]}"
        else:
            raise McdpValueError("Invalid rotation data.")


_case_register: Dict[str, Type["_Case"]] = {}    


class _Case(McdpBaseModel):

    def __init_subclass__(cls, *, type: str) -> None:
        _case_register[type] = cls
        super().__init_subclass__()


class BlockCase(_Case, type="block"):
    pos: Position
    block: str

    def __init__(self, pos: Union[str, Position], block: str) -> None:
        super().__init__(pos=pos, block=block)

    def __str__(self) -> str:
        return f"block {self.pos} {self.block}"


class BlocksCase(_Case, type="blocks"):
    start: Position
    end: Position

    destination: Position

    scan_mode: Literal["all", "marked"]

    def __init__(
            self,
            start: Union[str, Position],
            end: Union[str, Position],
            destination: Union[str, Position],
            *,
            scan_mode: Literal["all", "marked"] = "all"
    ) -> None:
        super().__init__(start=start, end=end, destination=destination, scan_mode=scan_mode)

    def __str__(self) -> str:
        return f"blocks {self.start} {self.end} {self.destination} {self.scan_mode}"


class DataCase(_Case, type="data"):
    type: Literal["block", "entity", "storage"]
    pos: Optional[Position] = None
    targets: Union[str, Selector, None] = None
    path: NBTPath

    def __init__(
            self,
            type: Literal["block", "entity", "storage"],
            pos_or_targets: Union[Position, str, Selector],
            path: Union[str, NBTPath]
    ) -> None:
        if type == "block":
            super().__init__(type=type, pos=pos_or_targets, path=path)
        else:
            super().__init__(type=type, targets=pos_or_targets, path=path)

    def __str__(self) -> str:
        if type == "block":
            return f"data block {self.pos} {self.path}"
        else:
            return f"data {self.type} {self.targets} {self.path}"


class EntityCase(_Case, type="entity"):
    targets: Union[str, Selector]

    def __init__(self, targets: Union[str, Selector]) -> None:
        super().__init__(targets=targets)

    def __str__(self) -> str:
        return f"entity {self.targets}"


class PredicateCase(_Case, type="predicate"):
    predicate: str

    def __init__(self, predicate: str) -> None:
        super().__init__(predicate=predicate)

    def __str__(self) -> str:
        return f"predicate {self.predicate}"


class ScoreCase(_Case, type="score"):
    target: Union[str, Selector]
    target_obj: str
    ops: Literal["<", "<=", "=", ">=", ">", "matches"]
    source: Union[str, Selector, None] = None
    source_obj: Optional[str] = None
    range: Optional[str] = None

    def __init__(
            self,
            target: Union[str, Selector],
            target_obj: str,
            ops: Literal["<", "<=", "=", ">=", ">", "matches"],
            source_or_range: Union[str, Selector],
            source_obj: Optional[str] = None
    ) -> None:
        if ops == "matches":
            if source_obj:
                raise McdpValueError("Invalid source objective.")
            super().__init__(
                    target=target,
                    target_obj=target_obj,
                    ops=ops,
                    range=source_or_range
            )
        else:
            super().__init__(
                    target=target,
                    target_obj=target_obj,
                    ops=ops,
                    source=source_or_range,
                    source_obj=source_obj
            )

    def __str__(self) -> str:
        if self.ops == "matches":
            return f"score {self.target} {self.target_obj} " +\
                f"{self.ops} {self.range}"
        else:
            return f"score {self.target} {self.target_obj} " +\
                f"{self.ops} {self.source} {self.source_obj}"


class ConditionInstruction(Instruction):
    unless: bool
    case: _Case

    def __init__(self, case: _Case, *, unless: bool = False) -> None:
        McdpBaseModel.__init__(self, case=case, unless=unless)

    def __str__(self) -> str:
        if self.unless:
            return f"unless {self.case}"
        else:
            return f"if {self.case}"


T_C_type = Literal["byte", "short", "int", "long", "float", "double"]

_store_register: Dict[str, Type["StoreMode"]] = {}


class StoreMode(McdpBaseModel):

    def __init__(self, **data) -> None:
        super().__init__(**data)

    def __new__(cls, type: str, *args, **kwds) -> "StoreMode":
        return _store_register[type](*args, **kwds)

    def __init_subclass__(cls, *, type: str) -> None:
        _store_register[type] = cls
        super().__init_subclass__()


class BlockStore(StoreMode, type="block"):
    target_pos: Position
    path: NBTPath
    type: T_C_type
    scale: float

    def __init__(
            self,
            target_pos: Union[str, Position],
            path: Union[str, NBTPath],
            type: T_C_type,
            scale: float
    ) -> None:
        super().__init__(target_pos=target_pos, path=path, type=type, scale=scale)

    def __str__(self) -> str:
        return f"block {self.target_pos} {self.path} {self.type} {self.scale}"


class BossbarStore(StoreMode, type="bossbar"):
    id: str
    value: Literal["value", "max"]

    def __init__(self, id: str, value: Literal["value", "max"]) -> None:
        super().__init__(id=id, value=value)

    def __str__(self) -> str:
        return f"bossbar {self.id} {self.value}"


class EntityStore(StoreMode, type="entity"):
    target: Union[str, Selector]
    path: NBTPath
    type: T_C_type
    scale: float

    def __init__(
            self,
            target: Union[str, Selector],
            path: Union[str, NBTPath],
            type: T_C_type,
            scale: float
    ) -> None:
        super().__init__(target=target, path=path, type=type, scale=scale)

    def __str__(self) -> str:
        return f"entity {self.target} {self.path} {self.type} {self.scale}"


class ScoreStore(StoreMode, type="score"):
    targets: Union[str, Selector]
    objective: str

    def __init__(self, targets: Union[str, Selector], objective: str) -> None:
        super().__init__(targets=targets, objective=objective)

    def __str__(self) -> str:
        return f"score {self.targets} {self.objective}"


class StorageStore(StoreMode, type="storage"):
    target: str
    path: NBTPath
    type: T_C_type
    scale: float

    def __init__(
            self,
            target: str,
            path: Union[str, NBTPath],
            type: T_C_type,
            scale: float
    ) -> None:
        super().__init__(target=target, path=path, type=type, scale=scale)

    def __str__(self) -> str:
        return f"storage {self.target} {self.path} {self.type} {self.scale}"


class StoreInstruction(Instruction):
    store_success: bool
    mode: StoreMode

    def __init__(self, mode: StoreMode, *, store_success: bool = False) -> None:
        McdpBaseModel.__init__(self, mode=mode, store_success=store_success)

    def __str__(self) -> str:
        if self.store_success:
            return f"store success {self.mode}"
        else:
            return f"store result {self.mode}"


class ContextExecEnv(ContextEnv):

    __slots__ = ["exec"]

    def __init__(self, exec: "Execute") -> None:
        self.exec = exec
        super().__init__("execute")
    
    def init(self) -> None:
        super().init()
        comment("This is a extra env file.")
        newline(2)
    
    def decorate_command(self, cmd: str) -> str:
        return self.exec.command_prefix() + cmd


class Execute(McdpVar):

    __slots__ = ["instructions", "env"]

    def __init__(self, instruction_or_execobj: Union[Instruction, "Execute"], *instructions: Union[Instruction, "Execute"]) -> None:
        if isinstance(instruction_or_execobj, Instruction):
            self.instructions = [instruction_or_execobj]
        else:
            self.instructions = instruction_or_execobj.instructions
        for i in instructions:
            if isinstance(i, Instruction):
                self.instructions.append(i)
            else:
                self.instructions.extend(i.instructions)
        self.env = ContextExecEnv(self)

    def __call__(self, command: Optional[str] = None) -> None:
        exc = "execute " + " ".join((str(i) for i in self.instructions))
        if not command:
            if not isinstance(self.instructions[-1], ConditionInstruction):
                raise McdpCommandError(
                        "execute", TypeError(
                                "Final instruction should be a conditon instruction."
                        ))
            insert(exc)
        else:
            insert(f"{exc} run {command}")
    
    def command_prefix(self) -> str:
        return "execute {0} run ".format(" ".join((str(i) for i in self.instructions)))

    def __enter__(self) -> "Execute":
        Context.add_env(self.env)
        return self
    
    def __exit__(self, exc_type, exc_ins, traceback) -> None:
        Context.pop_env()
    
    async def __aenter__(self) -> Context:
        context = self.env.creat_stream()
        return await context.__aenter__()
    
    async def __aexit__(self, exc_type, exc_ins, traceback) -> None:
        await Context.top.__aexit__(exc_type, exc_ins, traceback)

    def __str__(self) -> str:
        return f"Execute{tuple(self.instructions)}"

    __repr__ = __str__


def case(type: str, *args, **kwds) -> _Case:
    return _case_register[type](*args, **kwds)


class ContextLibEnv(ContextEnv):

    __slots__ = ["func"]

    def __init__(self, func: Callable[[], Optional[Coroutine]]) -> None:
        self.func = func
        super().__init__("Library")

    def init(self) -> None:
        comment(
            f"Library function {self.func.__name__} of Mcdp.",
        )
        newline()


class Function(McdpVar):
    """
    This class is only used to create library.
    If you want to define a normal function, use 
    mcdp.mcfunc.MCFunction or mcdp.mcfunc.mcfunc instead.
    """

    __slots__ = ["func", "space"]

    collection: Dict[str, "Function"] = {}

    def __init__(self, func: Callable[[], Union[None, Coroutine]], *,  space: Optional[str] = None) -> None:
        self.func = func
        self.space = space
        self.__class__.collection[func.__name__] = self
    
    def __call__(self, namespace: Optional[str] = None) -> None:
        namespace = namespace or get_config().namespace

        name = self.func.__name__
        if not self.space or self.space == '.':
            insert(f"function {namespace}:{name}")
        else:
            insert(f"function {namespace}:{self.space}/{name}")
    
    async def apply(self) -> None:
        if self.space:
            Context.enter_space(self.space)
        async with Context(self.func.__name__, envs=[ContextLibEnv(self.func)]):
            if iscoroutinefunction(self.func):
                await self.func()
            else:
                self.func()
        if self.space:
            Context.exit_space()


def lib_func(space: str = "libs") -> Callable[[Callable[[], Union[None, Coroutine]]], Function]:
    return partial(Function, space=space)


class IOStreamObject(McdpVar):

    __slots__ = ["data", "base"]

    data: List[str]

    def __init__(self, data: Optional[List[str]] = None, *, base: bool = False):
        if not data:
            data = []
        self.data = data
        self.base = base

    def __getitem__(self, value: Any):
        if self.base:
            self = self.copy()

        self.data.append(value)
        return self
    
    def copy(self):
        return self.__class__(self.data.copy())


class Printer(IOStreamObject):

    __slots__ = []

    input: List[MCString]

    def __init__(self, data: Optional[List[str]] = None, *, base: bool = False):
        super().__init__(data, base=base)
        self.input = []

    def __lshift__(self, other: Any) -> "Printer":
        if isinstance(other, PrinterEOF):
            other(self)
        else:
            if not isinstance(other, MCString):
                other = MCString.validate(other)

            self.input.append(other)
        return self


class PrinterEOF(IOStreamObject):

    __slots__ = []

    def __call__(self, stream: Printer) -> None:
        if len(stream.input) < 1:
            raise McdpCommandError(
                    "tellraw", ValueError(
                            "No string griven."
                    ))
        elif len(stream.input) == 1:
            input = stream.input[0]
        else:
            input = "[{0}]".format(','.join((str(i) for i in stream.input)))

        if not stream.data:
            self.__apply_printer__("tellraw {targets} {input}", input=input)
        elif len(stream.data) == 1:
            self.__apply_printer__("title {targets} {subcmd} {input}", input=input, subcmd=stream.data[0])
        else:
            raise McdpCommandError(
                "tellraw/title", ValueError(
                        "Invalid printer data."
                ))

        stream.input.clear()

    def __apply_printer__(self, cmd: str, **kw) -> None:
        if len(self.data) == 0:
            targets = "@a"
        elif len(self.data) == 1:
            targets = self.data[0]
        else:
            raise McdpCommandError(
                    "tellraw/title", ValueError(
                            "Invalid EOF data."
                    ))
        insert(cmd.format(targets=targets, **kw))


cout = Printer(base=True)
endl = PrinterEOF(base=True)


class McdpCommandError(McdpError):
    
    __slots__ = ["command"]

    def __init__(self, command: str, *arg: Exception) -> None:
        self.command = command
        if not arg:
            msg = f"Fail to handle command {command}."
        else:
            s = StringIO(f"During handle command {command}, {len(arg)} error(s) occur:\n")
            for err in arg:
                s.write(f"    {err.__class__.__qualname__}: {' '.join(err.args)}\n")
            msg = s.getvalue()
            s.close()
        super().__init__(msg)
