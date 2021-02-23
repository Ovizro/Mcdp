import ujson
from typing import Any, Dict

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
        criteria: str = "dummy",
        display: dict
    ):
        self.name = name
        self.criteria = criteria
        self.display = display
        
        self.counter = Counter()
