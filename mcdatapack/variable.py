import ujson
from typing import Any, Dict, Optional

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

	__slots__ = ["counter",]

	def __init__(self) -> None:
		self.counter = Counter()

class ScoreboardType(Variable):

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

		self.counter = Counter()

	def dumps(self) -> Optional[str]:
		if not self.counter:
			return
		
		if self.displayName:
			return "scoreboard objectives add {0} {1} {2}".format(
				self.name, self.criteria, ujson.dumps(self.displayName)
			)
		else:
			return "scoreboard objectives add {0} {1}".format(
				self.name, self.criteria
			)

	def remove(self) -> str:
		return f"scoreboard objectives remove {self.name}"

	def display(self, pos: str) -> str:
		return 