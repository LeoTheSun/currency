from dataclasses import dataclass


@dataclass(frozen=True)
class Parameter:
    Id: int = None
    Name: str = None
    Value: str = None