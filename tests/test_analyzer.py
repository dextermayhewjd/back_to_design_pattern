"""Tests for AST pattern & code smell analyzer engine."""

import json
from pathlib import Path

import pytest

from design_patterns.analyzer import (
    AnalysisReport,
    CodebaseAnalyzer,
    CodeSmell,
    PatternMatch,
)


# =====================================================================
# Data Model Tests
# =====================================================================

def test_pattern_match_dataclass():
    match = PatternMatch(
        pattern_id="visitor",
        pattern_name="Visitor",
        category="behavioral",
        file_path="sample.py",
        line_number=10,
        evidence="Class 'NodeVisitor' implements accept method",
    )
    assert match.pattern_id == "visitor"
    assert match.confidence == "high"


def test_code_smell_dataclass():
    smell = CodeSmell(
        smell_type="SINGLE_METHOD_CLASS",
        file_path="sample.py",
        line_number=5,
        description="Class 'Runner' has only 1 public method",
        recommended_pattern="strategy",
        target_version_baseline="Python 3.10+ (first-class functions / Callable)",
        refactoring_tip="Replace single-method class with a plain function or Callable strategy.",
    )
    assert smell.smell_type == "SINGLE_METHOD_CLASS"
    assert smell.recommended_pattern == "strategy"


def test_analysis_report_to_dict_json_serializable():
    report = AnalysisReport(
        files_scanned=2,
        total_lines=50,
        detected_patterns=[
            PatternMatch(
                pattern_id="visitor",
                pattern_name="Visitor",
                category="behavioral",
                file_path="a.py",
                line_number=1,
                evidence="accept method found",
            )
        ],
        code_smells=[
            CodeSmell(
                smell_type="SINGLE_METHOD_CLASS",
                file_path="b.py",
                line_number=10,
                description="single method class",
                recommended_pattern="strategy",
                target_version_baseline="Python 3.10+ (first-class functions / Callable)",
                refactoring_tip="Replace single-method class with a plain function or Callable strategy.",
            )
        ],
        syntax_errors=["bad.py: invalid syntax"],
    )
    data = report.to_dict()
    assert data["files_scanned"] == 2
    assert data["total_lines"] == 50
    assert len(data["detected_patterns"]) == 1
    assert len(data["code_smells"]) == 1
    assert len(data["syntax_errors"]) == 1

    # Verify JSON serialization
    serialized = json.dumps(data)
    loaded = json.loads(serialized)
    assert loaded["files_scanned"] == 2
    assert loaded["detected_patterns"][0]["pattern_id"] == "visitor"
    assert loaded["code_smells"][0]["smell_type"] == "SINGLE_METHOD_CLASS"


# =====================================================================
# Code Smell Detector Tests
# =====================================================================

def test_detect_single_method_class_smell():
    source = """
class ShippingCostCalculator:
    def __init__(self, rate: float):
        self.rate = rate

    def execute(self, weight: float) -> float:
        return self.rate * weight
"""
    analyzer = CodebaseAnalyzer()
    patterns, smells = analyzer.analyze_source(source, "shipping.py")
    matching = [s for s in smells if s.smell_type == "SINGLE_METHOD_CLASS"]
    assert len(matching) == 1
    assert matching[0].recommended_pattern == "strategy"
    assert "Python 3.10+" in matching[0].target_version_baseline
    assert "plain function or Callable" in matching[0].refactoring_tip


def test_single_method_class_without_init():
    source = """
class TaxCalculator:
    def execute(self, amount: float) -> float:
        return amount * 0.1
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source)
    assert any(s.smell_type == "SINGLE_METHOD_CLASS" for s in smells)


def test_multi_method_class_not_flagged_as_single_method():
    source = """
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def total(self):
        return sum(item.price for item in self.items)
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source)
    assert not any(s.smell_type == "SINGLE_METHOD_CLASS" for s in smells)


def test_dataclass_with_to_dict_not_flagged_as_single_method():
    source = """
from dataclasses import dataclass

@dataclass
class AnalysisReport:
    files_scanned: int
    total_lines: int

    def to_dict(self) -> dict:
        return {"files_scanned": self.files_scanned, "total_lines": self.total_lines}
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source)
    assert not any(s.smell_type == "SINGLE_METHOD_CLASS" for s in smells)


def test_dataclass_with_args_and_helper_not_flagged_as_single_method():
    source = """
from dataclasses import dataclass

@dataclass(slots=True, kw_only=True)
class UserProfile:
    username: str

    def format_display(self) -> str:
        return f"User: {self.username}"
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source)
    assert not any(s.smell_type == "SINGLE_METHOD_CLASS" for s in smells)


def test_annotated_fields_class_not_flagged_as_single_method():
    source = """
class DataRecord:
    name: str
    count: int

    def summarize(self) -> str:
        return f"{self.name}: {self.count}"
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source)
    assert not any(s.smell_type == "SINGLE_METHOD_CLASS" for s in smells)


def test_detect_parameter_explosion_smell():
    source = """
class ServerConfig:
    def __init__(self, host, port, timeout, max_conns, retries, ssl, cert):
        pass
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source, "server.py")
    matching = [s for s in smells if s.smell_type == "PARAMETER_EXPLOSION"]
    assert len(matching) == 1
    assert matching[0].recommended_pattern in ("builder", "dataclass")
    assert "Python 3.10+" in matching[0].target_version_baseline
    assert "@dataclass with kw_only=True" in matching[0].refactoring_tip


def test_function_parameter_explosion_excludes_self_and_cls():
    # 5 parameters excluding self -> should NOT trigger (> 5 required)
    source = """
class Worker:
    def process(self, a, b, c, d, e):
        pass
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source)
    assert not any(s.smell_type == "PARAMETER_EXPLOSION" for s in smells)


def test_standalone_function_parameter_explosion():
    # 6 parameters in standalone function -> triggers
    source = """
def create_pipeline(src, dest, batch_size, transform_fn, filter_fn, error_handler):
    pass
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source)
    assert any(s.smell_type == "PARAMETER_EXPLOSION" for s in smells)


def test_detect_complex_branching_smell():
    source = """
def handle_command(command: str):
    if command == "start":
        return 1
    elif command == "stop":
        return 2
    elif command == "pause":
        return 3
    elif command == "resume":
        return 4
    else:
        return 0
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source, "handler.py")
    matching = [s for s in smells if s.smell_type == "COMPLEX_BRANCHING"]
    assert len(matching) == 1
    assert matching[0].recommended_pattern in ("strategy", "match-case")
    assert "Python 3.10+" in matching[0].target_version_baseline
    assert "Structural Pattern Matching" in matching[0].target_version_baseline
    assert "match-case or Strategy pattern" in matching[0].refactoring_tip


def test_simple_branching_not_flagged():
    source = """
def status(val):
    if val > 10:
        return "high"
    elif val > 5:
        return "medium"
    else:
        return "low"
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source)
    assert not any(s.smell_type == "COMPLEX_BRANCHING" for s in smells)


def test_detect_manual_iterator_smell():
    source = """
class CounterIterator:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        val = self.current
        self.current += 1
        return val
"""
    analyzer = CodebaseAnalyzer()
    _, smells = analyzer.analyze_source(source, "iter.py")
    matching = [s for s in smells if s.smell_type == "MANUAL_ITERATOR"]
    assert len(matching) == 1
    assert matching[0].recommended_pattern == "iterator"
    assert "Python 3.10+" in matching[0].target_version_baseline
    assert "generator function using yield" in matching[0].refactoring_tip


# =====================================================================
# Design Pattern Detector Tests
# =====================================================================

def test_detect_visitor_pattern():
    source = """
class ExpressionNode:
    def accept(self, visitor):
        return visitor.visit_expression(self)

class TreeVisitor:
    def visit_expression(self, node):
        pass
    def visit_literal(self, node):
        pass
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "visitor.py")
    matching = [p for p in patterns if p.pattern_id == "visitor"]
    assert len(matching) >= 1
    assert all(p.category == "behavioral" for p in matching)


def test_detect_singleton_pattern_new_override():
    source = """
class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "db.py")
    matching = [p for p in patterns if p.pattern_id == "singleton"]
    assert len(matching) == 1
    assert matching[0].category == "creational"


def test_detect_singleton_pattern_metaclass():
    source = """
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ConfigRegistry(metaclass=SingletonMeta):
    pass
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "meta.py")
    matching = [p for p in patterns if p.pattern_id == "singleton"]
    assert len(matching) >= 1


def test_detect_composite_pattern():
    source = """
class GraphicGroup:
    def __init__(self):
        self.children = []

    def add(self, graphic):
        self.children.append(graphic)

    def remove(self, graphic):
        self.children.remove(graphic)

    def draw(self):
        for child in self.children:
            child.draw()
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "composite.py")
    matching = [p for p in patterns if p.pattern_id == "composite"]
    assert len(matching) == 1
    assert matching[0].category == "structural"


def test_detect_decorator_pattern():
    source = """
class LoggingDecorator:
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def execute(self):
        print("start")
        result = self._wrapped.execute()
        print("end")
        return result
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "decorator.py")
    matching = [p for p in patterns if p.pattern_id in ("decorator", "proxy")]
    assert len(matching) >= 1
    assert all(p.category == "structural" for p in matching)


def test_detect_proxy_pattern():
    source = """
class SecureProxy:
    def __init__(self, real_subject):
        self._real_subject = real_subject

    def request(self):
        if self._check_access():
            return self._real_subject.request()
        raise PermissionError

    def _check_access(self):
        return True
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "proxy.py")
    matching = [p for p in patterns if p.pattern_id == "proxy"]
    assert len(matching) == 1
    assert matching[0].category == "structural"


def test_detect_observer_pattern():
    source = """
class EventDispatcher:
    def __init__(self):
        self._listeners = []

    def subscribe(self, listener):
        self._listeners.append(listener)

    def unsubscribe(self, listener):
        self._listeners.remove(listener)

    def notify(self, event):
        for listener in self._listeners:
            listener(event)
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "observer.py")
    matching = [p for p in patterns if p.pattern_id == "observer"]
    assert len(matching) == 1
    assert matching[0].category == "behavioral"


def test_detect_template_method_pattern():
    source = """
from abc import ABC, abstractmethod

class DataMiner(ABC):
    def mine(self, path: str):
        data = self.read_data(path)
        parsed = self.parse_data(data)
        self.export(parsed)

    @abstractmethod
    def read_data(self, path: str):
        pass

    @abstractmethod
    def parse_data(self, raw_data):
        pass

    def export(self, data):
        print("Exporting:", data)
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "miner.py")
    matching = [p for p in patterns if p.pattern_id == "template_method"]
    assert len(matching) == 1
    assert matching[0].category == "behavioral"


def test_detect_strategy_pattern():
    source = """
from typing import Callable

class PaymentContext:
    def __init__(self, strategy: Callable[[float], bool]):
        self._strategy = strategy

    def execute_payment(self, amount: float) -> bool:
        return self._strategy(amount)
"""
    analyzer = CodebaseAnalyzer()
    patterns, _ = analyzer.analyze_source(source, "payment.py")
    matching = [p for p in patterns if p.pattern_id == "strategy"]
    assert len(matching) == 1
    assert matching[0].category == "behavioral"


# =====================================================================
# Path / Directory Scanning Tests
# =====================================================================

def test_analyze_single_file(tmp_path):
    py_file = tmp_path / "calc.py"
    py_file.write_text("""
class RateCalculator:
    def __init__(self, r):
        self.r = r
    def calculate(self, x):
        return self.r * x
""")
    analyzer = CodebaseAnalyzer()
    report = analyzer.analyze_path(py_file)
    assert report.files_scanned == 1
    assert report.total_lines > 0
    assert any(s.smell_type == "SINGLE_METHOD_CLASS" for s in report.code_smells)
    assert len(report.syntax_errors) == 0


def test_analyze_directory_recursive(tmp_path):
    sub1 = tmp_path / "sub1"
    sub1.mkdir()
    (sub1 / "a.py").write_text("""
class A:
    def __init__(self, x):
        self.x = x
    def run(self):
        return self.x
""")
    sub2 = tmp_path / "sub2"
    sub2.mkdir()
    (sub2 / "b.py").write_text("""
def process(a, b, c, d, e, f, g):
    pass
""")
    analyzer = CodebaseAnalyzer()
    report = analyzer.analyze_path(tmp_path)
    assert report.files_scanned == 2
    assert any(s.smell_type == "SINGLE_METHOD_CLASS" for s in report.code_smells)
    assert any(s.smell_type == "PARAMETER_EXPLOSION" for s in report.code_smells)


def test_analyze_ignores_hidden_and_pycache(tmp_path):
    # Visible valid file
    visible_dir = tmp_path / "app"
    visible_dir.mkdir()
    (visible_dir / "valid.py").write_text("x = 1\n")

    # .git directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "ignored.py").write_text("broken syntax ((\n")

    # .venv directory
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "ignored2.py").write_text("broken syntax ((\n")

    # __pycache__ directory
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "ignored3.py").write_text("broken syntax ((\n")

    analyzer = CodebaseAnalyzer()
    report = analyzer.analyze_path(tmp_path)
    assert report.files_scanned == 1
    assert len(report.syntax_errors) == 0


def test_analyze_syntax_error_handling(tmp_path):
    broken_file = tmp_path / "broken.py"
    broken_file.write_text("def broken_syntax(:")
    analyzer = CodebaseAnalyzer()
    report = analyzer.analyze_path(tmp_path)
    assert len(report.syntax_errors) == 1
    assert "broken.py" in report.syntax_errors[0]


def test_analyze_nonexistent_path_raises_filenotfound():
    analyzer = CodebaseAnalyzer()
    with pytest.raises(FileNotFoundError):
        analyzer.analyze_path(Path("/nonexistent/path/that/does/not/exist.py"))
