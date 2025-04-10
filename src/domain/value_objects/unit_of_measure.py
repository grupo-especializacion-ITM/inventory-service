from dataclasses import dataclass
from enum import Enum, auto


class UnitType(Enum):
    """Types of units of measure"""
    WEIGHT = auto()
    VOLUME = auto()
    UNIT = auto()


@dataclass(frozen=True)
class UnitOfMeasure:
    """Value object representing a unit of measure"""
    unit: str
    
    # Mapping of units to their types
    _UNIT_TYPES = {
        # Weight units
        "g": UnitType.WEIGHT,
        "kg": UnitType.WEIGHT,
        "lb": UnitType.WEIGHT,
        "oz": UnitType.WEIGHT,
        
        # Volume units
        "ml": UnitType.VOLUME,
        "l": UnitType.VOLUME,
        "gal": UnitType.VOLUME,
        "fl_oz": UnitType.VOLUME,
        "cup": UnitType.VOLUME,
        "tbsp": UnitType.VOLUME,
        "tsp": UnitType.VOLUME,
        
        # Count units
        "unit": UnitType.UNIT,
        "piece": UnitType.UNIT,
        "slice": UnitType.UNIT,
        "whole": UnitType.UNIT,
    }
    
    # Conversion factors to base units (g for weight, ml for volume)
    _CONVERSION_FACTORS = {
        # Weight units (to grams)
        "g": 1.0,
        "kg": 1000.0,
        "lb": 453.592,
        "oz": 28.3495,
        
        # Volume units (to milliliters)
        "ml": 1.0,
        "l": 1000.0,
        "gal": 3785.41,
        "fl_oz": 29.5735,
        "cup": 236.588,
        "tbsp": 14.7868,
        "tsp": 4.92892,
        
        # Count units
        "unit": 1.0,
        "piece": 1.0,
        "slice": 1.0,
        "whole": 1.0,
    }
    
    def __post_init__(self):
        if self.unit not in self._UNIT_TYPES:
            raise ValueError(f"Unknown unit of measure: {self.unit}")
    
    @property
    def unit_type(self) -> UnitType:
        """Get the type of unit (weight, volume, unit)"""
        return self._UNIT_TYPES[self.unit]
    
    def is_compatible_with(self, other: "UnitOfMeasure") -> bool:
        """Check if this unit is compatible with another unit"""
        return self.unit_type == other.unit_type
    
    def convert_to(self, quantity: float, target_unit: str) -> float:
        """Convert a quantity from this unit to another compatible unit"""
        if target_unit not in self._UNIT_TYPES:
            raise ValueError(f"Unknown target unit: {target_unit}")
        
        if self.unit_type != self._UNIT_TYPES[target_unit]:
            raise ValueError(f"Cannot convert {self.unit} to {target_unit} (incompatible types)")
        
        # Convert to base unit first, then to target unit
        base_value = quantity * self._CONVERSION_FACTORS[self.unit]
        target_value = base_value / self._CONVERSION_FACTORS[target_unit]
        
        return target_value