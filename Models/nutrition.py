from dataclasses import dataclass


@dataclass
class Nutrition:
    label:str
    value:str
    unit:str
    daily:str