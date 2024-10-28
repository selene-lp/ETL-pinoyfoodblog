from dataclasses import dataclass
from .ingredient import Ingredient


@dataclass
class Recipe:
    name: str
    link: str
    thumbnail: str
    description: str
    publish: str
    modified: str
    categories: list[str]
    tags: list[str]
    courses: list[str]
    cuisines: list[str]
    prep_time: str
    cook_time: str
    custom_time: list[str]
    good_for: list
    ingredients: list[Ingredient]
    instructions: list[str]
    nutritions: list[str]
