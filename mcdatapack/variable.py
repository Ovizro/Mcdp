import ujson
from typing import Any, Dict, Final, Optional, Union

from .output_stream import MCFunc

class Counter:
	
	__slots__ = ["_count",]
	
	def __init__(self):
		self._count = 0
	
	def __pos__(self) -> None:
		self._count += 1
		
	def __neg__(self) -> None:
		self._count -= 1
		
	def __invert__(self) -> None:
		self._count = 0
		
	def __bool__(self) -> bool:
		if self._count > 0:
			return True
		else:
			return False

class Variable:

	__slots__ = ["counter", "linked"]

	def __init__(self) -> None:
		self.counter = Counter()
		self.linked = set()

	def link(self, var: Union["Variable", Counter]) -> None:
		if isinstance(var, self.__class__):
			var: Final[Counter] = var.counter
		if var.counter == self.counter:
			raise RuntimeError("try to link a var to itself.")
		self.linked.add(var)

	def unlink(self, var: Union["Variable", Counter]) -> None:
		if isinstance(var, self.__class__):
			var: Counter = var.counter
		if var.counter == self.counter:
			raise RuntimeError("try to unlink a var from itself.")
		self.linked.remove(var)

class ScoreboardType(Variable):

	__slots__ = ["name", "criteria", "displayName", "counter", "linked"]

	def __init__(
		self,
		name: str,
		*,
		criteria: str = "dummy",
		display: Optional[dict] = None,
	):
		self.name = name
		self.criteria = criteria
		self.displayName = display

		super().__init__()

	def dumps(self) -> Optional[str]:
		if self.displayName:
			return "scoreboard objectives add {0} {1} {2}\n".format(
				self.name, self.criteria, ujson.dumps(self.displayName)
			)
		else:
			return "scoreboard objectives add {0} {1}\n".format(
				self.name, self.criteria
			)
	
	def dump(self) -> None:
		MCFunc.write(self.dumps())

	def remove(self) -> None:
		MCFunc.write(f"scoreboard objectives remove {self.name}\n")

	def display(self, pos: str) -> None:
		MCFunc.write(f"scoreboard objectives setdisplay {pos} {self.name}\n")

class ScoreType(ScoreboardType):

	__slots__ = ["name", "criteria", "displayName", "counter", "linked", "player"]

	def __init__(self, name: str, player: str = "#mcdp_main", *, criteria: str = "dummy", display: Optional[dict] = None):
		self.player = player
		super().__init__(name, criteria=criteria, display=display)

	def __add__(self, other: Union[int, "ScoreType"]) -> "ScoreType":
		+self.counter
		if isinstance(other, int):
			MCFunc.write()