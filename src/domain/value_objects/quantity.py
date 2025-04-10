from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    """Value object representing a quantity of something"""
    value: float
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Quantity cannot be negative")
    
    def __add__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value + other.value)
        elif isinstance(other, (int, float)):
            return Quantity(self.value + other)
        else:
            raise TypeError(f"Cannot add Quantity and {type(other)}")
    
    def __sub__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value - other.value)
        elif isinstance(other, (int, float)):
            return Quantity(self.value - other)
        else:
            raise TypeError(f"Cannot subtract {type(other)} from Quantity")
    
    def __eq__(self, other):
        if isinstance(other, Quantity):
            return self.value == other.value
        elif isinstance(other, (int, float)):
            return self.value == other
        else:
            return False
    
    def __lt__(self, other):
        if isinstance(other, Quantity):
            return self.value < other.value
        elif isinstance(other, (int, float)):
            return self.value < other
        else:
            raise TypeError(f"Cannot compare Quantity and {type(other)}")
    
    def __gt__(self, other):
        if isinstance(other, Quantity):
            return self.value > other.value
        elif isinstance(other, (int, float)):
            return self.value > other
        else:
            raise TypeError(f"Cannot compare Quantity and {type(other)}")