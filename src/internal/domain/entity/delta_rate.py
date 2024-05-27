from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class DeltaRate:
    Id: int = None
    Date: date = None
    Delta: Decimal = None
    Code: str = None