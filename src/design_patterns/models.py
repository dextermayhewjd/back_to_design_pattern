"""Domain models for Design Patterns."""

from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"


@dataclass
class Pattern:
    id: str
    name: str
    chinese_name: str
    category: Category
    intent: str
    problem: str
    solution: str
    applicability: list[str] = field(default_factory=list)
    symptoms: list[str] = field(default_factory=list)
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    conceptual_code: str = ""
    realworld_code: str = ""
    scaffold_template: str = ""
