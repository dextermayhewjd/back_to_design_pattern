"""Pattern registry storing and querying design patterns."""

from typing import Optional
from design_patterns.models import Category, Pattern


class PatternRegistry:
    def __init__(self) -> None:
        self._patterns: dict[str, Pattern] = {}

    def register(self, pattern: Pattern) -> None:
        self._patterns[pattern.id] = pattern

    def get(self, pattern_id: str) -> Optional[Pattern]:
        return self._patterns.get(pattern_id)

    def list_all(self, category: Optional[Category] = None) -> list[Pattern]:
        patterns = list(self._patterns.values())
        if category is not None:
            patterns = [p for p in patterns if p.category == category]
        return patterns

    def count(self) -> int:
        return len(self._patterns)
