import pytest
from design_patterns.models import Category, Pattern
from design_patterns.registry import PatternRegistry

def test_pattern_registry_register_and_get():
    registry = PatternRegistry()
    pattern = Pattern(
        id="factory-method",
        name="Factory Method",
        chinese_name="工厂方法",
        category=Category.CREATIONAL,
        intent="Provides an interface for creating objects in a superclass.",
        problem="Tight coupling to concrete product classes.",
        solution="Replace direct constructor calls with a factory method.",
        applicability=["When you don't know exact types beforehand"],
        symptoms=["tight coupling", "new keyword proliferation"],
        pros=["Avoids tight coupling", "Single Responsibility"],
        cons=["Can lead to many subclasses"],
        relations=["Abstract Factory"],
        conceptual_code="class Creator: pass",
        realworld_code="class Logistics: pass",
        scaffold_template="# Template"
    )
    registry.register(pattern)
    assert registry.count() == 1
    assert registry.get("factory-method") == pattern
    assert registry.get("non-existent") is None
    assert len(registry.list_all(Category.CREATIONAL)) == 1
    assert len(registry.list_all(Category.STRUCTURAL)) == 0
