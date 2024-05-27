from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ExchangeRate:
    Id: int = None
    Date: date = None
    Count: int = None
    Rate: Decimal = None
    Change: Decimal = None
    Code: str = None