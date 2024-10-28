from dataclasses import dataclass


@dataclass
class Ingredient:
    amount: str
    unit: str
    name: str
    notes: str
