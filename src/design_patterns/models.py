"""Domain models for Design Patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"


@dataclass
class VersionEvolution:
    version_tag: str        # e.g. "classic", "3.10+", "3.12+"
    summary: str            # 1-line summary of how pattern is implemented in this tier
    key_features: list[str] # Language features used (e.g. ["match-case", "dataclass(kw_only=True)"])
    code: str               # Complete runnable Python code for this tier
    line_count: int         # Line count of code


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
    classic_code: str = ""
    python310_code: str = ""
    python312_code: str = ""
    matrix_notes: dict[str, str] = field(default_factory=dict)
    scaffold_template: str = ""

    def __init__(
        self,
        id: str,
        name: str,
        chinese_name: str,
        category: Category,
        intent: str,
        problem: str,
        solution: str,
        applicability: list[str] | None = None,
        symptoms: list[str] | None = None,
        pros: list[str] | None = None,
        cons: list[str] | None = None,
        relations: list[str] | None = None,
        classic_code: str = "",
        python310_code: str = "",
        python312_code: str = "",
        matrix_notes: dict[str, str] | None = None,
        scaffold_template: str = "",
        conceptual_code: str | None = None,
        realworld_code: str | None = None,
        pythonic_code: str | None = None,
        pythonic_notes: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.chinese_name = chinese_name
        self.category = category
        self.intent = intent
        self.problem = problem
        self.solution = solution
        self.applicability = applicability if applicability is not None else []
        self.symptoms = symptoms if symptoms is not None else []
        self.pros = pros if pros is not None else []
        self.cons = cons if cons is not None else []
        self.relations = relations if relations is not None else []
        self.classic_code = classic_code or (conceptual_code or "")
        self.python310_code = python310_code or (realworld_code or "")
        self.python312_code = python312_code or (pythonic_code or "")
        self.matrix_notes = matrix_notes if matrix_notes is not None else {}
        if pythonic_notes and "3.10" not in self.matrix_notes:
            self.matrix_notes["3.10"] = pythonic_notes
        self.scaffold_template = scaffold_template

    @property
    def conceptual_code(self) -> str:
        return self.classic_code

    @conceptual_code.setter
    def conceptual_code(self, value: str) -> None:
        self.classic_code = value

    @property
    def realworld_code(self) -> str:
        return self.python310_code

    @realworld_code.setter
    def realworld_code(self, value: str) -> None:
        self.python310_code = value

    @property
    def pythonic_code(self) -> str:
        return self.python312_code or self.python310_code

    @pythonic_code.setter
    def pythonic_code(self, value: str) -> None:
        self.python312_code = value

    @property
    def pythonic_notes(self) -> str:
        return self.matrix_notes.get("3.10", "")

    def get_evolution(self, version: str) -> VersionEvolution:
        v = version.strip().lower()
        if v in ("classic", "legacy", "oop", "gof"):
            tag = "classic"
            key = "classic"
            code = self.classic_code
        elif v in ("3.10", "3.10+", "310", "py310", "modern", "pythonic"):
            tag = "3.10+"
            key = "3.10"
            code = self.python310_code
        elif v in ("3.12", "3.12+", "312", "py312", "nextgen"):
            tag = "3.12+"
            key = "3.12"
            code = self.python312_code
        else:
            raise ValueError(f"Unknown evolution version '{version}'. Expected 'classic', '3.10', or '3.12'.")

        note = self.matrix_notes.get(key, "")
        summary = note.splitlines()[0] if note else f"{self.name} ({tag})"

        key_features: list[str] = []
        if key == "classic":
            if "ABC" in code or "abstractmethod" in code:
                key_features.append("abc.ABC")
            if "class " in code:
                key_features.append("class inheritance")
        elif key == "3.10":
            if "match " in code and "case " in code:
                key_features.append("match-case")
            if "@dataclass" in code:
                key_features.append("dataclass")
            if " | " in code or " | None" in code:
                key_features.append("union types (|)")
            if "Callable" in code:
                key_features.append("Callable")
            if "Protocol" in code:
                key_features.append("Protocol")
            if "yield" in code:
                key_features.append("generator")
            if "@singledispatch" in code:
                key_features.append("@singledispatch")
        elif key == "3.12":
            if "[" in code and "]" in code and ("class " in code or "def " in code):
                key_features.append("PEP 695 generics")
            if "Self" in code:
                key_features.append("typing.Self")
            if "@override" in code:
                key_features.append("@override")
            if "@dataclass" in code:
                key_features.append("dataclass")

        if not key_features:
            if key == "classic":
                key_features = ["abc.ABC", "inheritance"]
            elif key == "3.10":
                key_features = ["type annotations", "dataclass", "modern idioms"]
            else:
                key_features = ["PEP 695 type parameters", "typing.Self"]

        lines = [line for line in code.strip().splitlines() if line.strip()]
        line_count = len(lines)

        return VersionEvolution(
            version_tag=tag,
            summary=summary,
            key_features=key_features,
            code=code,
            line_count=line_count,
        )
