from dataclasses import dataclass


@dataclass(frozen=True)
class CurrencyCode:
    Id: int = None
    Country: str = None
    Currency: str = None
    Code: str = None
    Number: int = None