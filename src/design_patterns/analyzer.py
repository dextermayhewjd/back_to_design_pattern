"""AST Pattern and Code Smell Analyzer Engine.

Detects classic design patterns and "Java-in-Python" anti-patterns across
Python source code using Python's standard library ast module.
"""

from __future__ import annotations

import ast
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class PatternMatch:
    """Represents a detected design pattern occurrence."""

    pattern_id: str
    pattern_name: str
    category: str
    file_path: str
    line_number: int
    evidence: str
    confidence: str = "high"  # "high" | "medium"


@dataclass
class CodeSmell:
    """Represents a detected code smell or anti-pattern."""

    smell_type: str  # e.g. "SINGLE_METHOD_CLASS", "PARAMETER_EXPLOSION", "COMPLEX_BRANCHING", "MANUAL_ITERATOR"
    file_path: str
    line_number: int
    description: str
    recommended_pattern: str
    target_version_baseline: str  # e.g. "Python 3.10+ (Structural Pattern Matching match-case)"
    refactoring_tip: str


@dataclass
class AnalysisReport:
    """Consolidated report of codebase patterns and code smells."""

    files_scanned: int
    total_lines: int
    detected_patterns: list[PatternMatch] = field(default_factory=list)
    code_smells: list[CodeSmell] = field(default_factory=list)
    syntax_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "files_scanned": self.files_scanned,
            "total_lines": self.total_lines,
            "detected_patterns": [asdict(p) for p in self.detected_patterns],
            "code_smells": [asdict(s) for s in self.code_smells],
            "syntax_errors": self.syntax_errors,
        }


class _ASTAnalyzerVisitor(ast.NodeVisitor):
    """Internal AST visitor to extract patterns and code smells."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.patterns: list[PatternMatch] = []
        self.smells: list[CodeSmell] = []
        self._seen_elifs: set[ast.If] = set()

    # ------------------------------------------------------------------
    # Class-level Analysis
    # ------------------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        methods = [
            m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        public_methods = [m for m in methods if not m.name.startswith("_")]
        method_names = {m.name for m in methods}

        # Check for smells
        self._check_single_method_class(node, methods, public_methods, method_names)
        self._check_manual_iterator(node, method_names)

        # Check for patterns
        self._check_visitor_pattern(node, methods)
        self._check_singleton_pattern(node, methods)
        self._check_composite_pattern(node, methods, method_names)
        self._check_decorator_proxy_pattern(node, methods)
        self._check_observer_pattern(node, method_names)
        self._check_template_method_pattern(node, methods)
        self._check_strategy_pattern(node, methods)

        # Continue traversing children
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Function-level Analysis
    # ------------------------------------------------------------------

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._analyze_function(node)
        self.generic_visit(node)

    def _analyze_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._check_parameter_explosion(node)
        self._check_complex_branching(node)

    # ------------------------------------------------------------------
    # Smell Checkers
    # ------------------------------------------------------------------

    def _check_single_method_class(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        public_methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        # Exclude exception classes and test cases
        is_exception_or_test = any(
            isinstance(b, ast.Name) and b.id in ("Exception", "BaseException", "TestCase")
            for b in node.bases
        )
        if is_exception_or_test:
            return

        # Exclude manual iterators (which define __iter__ and __next__)
        if "__iter__" in method_names and "__next__" in method_names:
            return

        # Class with exactly 1 public method (excluding visitor accept method)
        if len(public_methods) == 1:
            method_name = public_methods[0].name
            if method_name == "accept":
                return

            self.smells.append(
                CodeSmell(
                    smell_type="SINGLE_METHOD_CLASS",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    description=(
                        f"Class '{node.name}' has only 1 public method ('{method_name}'). "
                        "In Python, this is often better expressed as a plain function or Callable strategy."
                    ),
                    recommended_pattern="strategy",
                    target_version_baseline="Python 3.10+ (first-class functions / Callable)",
                    refactoring_tip="Replace single-method class with a plain function or Callable strategy.",
                )
            )

    def _check_parameter_explosion(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        posonly = [a.arg for a in node.args.posonlyargs]
        args = [a.arg for a in node.args.args]
        kwonly = [a.arg for a in node.args.kwonlyargs]
        all_params = posonly + args + kwonly

        # Exclude self and cls receiver parameters
        if all_params and all_params[0] in ("self", "cls"):
            params = all_params[1:]
        else:
            params = all_params

        if len(params) > 5:
            self.smells.append(
                CodeSmell(
                    smell_type="PARAMETER_EXPLOSION",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    description=f"Function/Method '{node.name}' has {len(params)} parameters (> 5).",
                    recommended_pattern="builder",
                    target_version_baseline="Python 3.10+ (dataclass(kw_only=True))",
                    refactoring_tip="Group parameters into a @dataclass with kw_only=True or use Builder.",
                )
            )

    def _check_complex_branching(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        # Collect if statements directly in this function (avoiding nested functions/classes)
        direct_ifs: list[ast.If] = []
        stack: list[ast.AST] = list(ast.iter_child_nodes(node))
        while stack:
            item = stack.pop()
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(item, ast.If):
                direct_ifs.append(item)
            stack.extend(ast.iter_child_nodes(item))

        for if_node in direct_ifs:
            if if_node in self._seen_elifs:
                continue

            # Trace if-elif chain
            branches = 1
            curr = if_node
            while len(curr.orelse) == 1 and isinstance(curr.orelse[0], ast.If):
                branches += 1
                curr = curr.orelse[0]
                self._seen_elifs.add(curr)

            if curr.orelse:
                branches += 1

            if branches > 3:
                self.smells.append(
                    CodeSmell(
                        smell_type="COMPLEX_BRANCHING",
                        file_path=self.file_path,
                        line_number=if_node.lineno,
                        description=f"Function '{node.name}' has complex branching with {branches} branches (> 3).",
                        recommended_pattern="strategy",
                        target_version_baseline="Python 3.10+ (Structural Pattern Matching match-case)",
                        refactoring_tip="Replace chained if-elif branches with match-case or Strategy pattern.",
                    )
                )

    def _check_manual_iterator(
        self, node: ast.ClassDef, method_names: set[str]
    ) -> None:
        if "__iter__" in method_names and "__next__" in method_names:
            self.smells.append(
                CodeSmell(
                    smell_type="MANUAL_ITERATOR",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    description=(
                        f"Class '{node.name}' implements manual iterator protocol (__iter__ and __next__). "
                        "Replace with generator yield."
                    ),
                    recommended_pattern="iterator",
                    target_version_baseline="Python 3.10+ (generator yield / yield from)",
                    refactoring_tip="Replace manual __iter__/__next__ class with a generator function using yield.",
                )
            )

    # ------------------------------------------------------------------
    # Pattern Checkers
    # ------------------------------------------------------------------

    def _check_visitor_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        has_accept = any(m.name == "accept" for m in methods)
        has_visit_methods = any(m.name.startswith("visit_") for m in methods)
        inherits_visitor = any(
            (isinstance(b, ast.Name) and "visitor" in b.id.lower())
            or (isinstance(b, ast.Attribute) and "visitor" in b.attr.lower())
            for b in node.bases
        )

        if has_accept or has_visit_methods or inherits_visitor:
            self.patterns.append(
                PatternMatch(
                    pattern_id="visitor",
                    pattern_name="Visitor",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements visitor interface (accept method or visit_* methods)",
                    confidence="high",
                )
            )

    def _check_singleton_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        # Check __new__ override with instance caching
        new_methods = [m for m in methods if m.name == "__new__"]
        has_singleton_new = False
        if new_methods:
            for sub in ast.walk(new_methods[0]):
                if isinstance(sub, ast.Name) and sub.id in (
                    "_instance",
                    "_instances",
                    "instance",
                    "instances",
                ):
                    has_singleton_new = True
                    break
                if isinstance(sub, ast.Attribute) and sub.attr in (
                    "_instance",
                    "_instances",
                    "instance",
                ):
                    has_singleton_new = True
                    break

            if not has_singleton_new:
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        for t in stmt.targets:
                            if isinstance(t, ast.Name) and t.id in ("_instance", "_instances"):
                                has_singleton_new = True
                                break

        # Check metaclass singleton
        is_metaclass = any(isinstance(b, ast.Name) and b.id == "type" for b in node.bases)
        has_call = any(m.name == "__call__" for m in methods)
        has_singleton_meta = is_metaclass and has_call

        # Check metaclass usage
        has_singleton_meta_kw = any(
            kw.arg == "metaclass"
            and isinstance(kw.value, ast.Name)
            and "singleton" in kw.value.id.lower()
            for kw in node.keywords
        )

        if has_singleton_new or has_singleton_meta or has_singleton_meta_kw:
            self.patterns.append(
                PatternMatch(
                    pattern_id="singleton",
                    pattern_name="Singleton",
                    category="creational",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' controls instance creation via __new__ or metaclass caching",
                    confidence="high",
                )
            )

    def _check_composite_pattern(
        self,
        node: ast.ClassDef,
        methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
        method_names: set[str],
    ) -> None:
        has_add = bool(method_names & {"add", "add_child", "add_component", "append"})
        has_remove = bool(method_names & {"remove", "remove_child", "remove_component"})

        if not (has_add and has_remove):
            return

        has_children_attr = False
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if isinstance(t, ast.Name) and any(
                        k in t.id.lower() for k in ("child", "children", "component")
                    ):
                        has_children_attr = True

        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            for sub in ast.walk(init_methods[0]):
                if isinstance(sub, ast.Attribute) and any(
                    k in sub.attr.lower() for k in ("child", "children", "component", "items")
                ):
                    has_children_attr = True
                    break

        name_lower = node.name.lower()
        if has_children_attr or "composite" in name_lower or "group" in name_lower:
            self.patterns.append(
                PatternMatch(
                    pattern_id="composite",
                    pattern_name="Composite",
                    category="structural",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements Composite pattern with add/remove child components",
                    confidence="high",
                )
            )

    def _check_decorator_proxy_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        wrapped_attrs: set[str] = set()
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            for sub in ast.walk(init_methods[0]):
                if isinstance(sub, ast.Assign):
                    for target in sub.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                        ):
                            attr_lower = target.attr.lower()
                            if any(
                                w in attr_lower
                                for w in (
                                    "wrapped",
                                    "component",
                                    "real_subject",
                                    "subject",
                                    "inner",
                                    "target",
                                    "decorated",
                                )
                            ):
                                wrapped_attrs.add(target.attr)

        delegates = False
        if wrapped_attrs:
            for m in methods:
                if m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if (
                        isinstance(sub, ast.Attribute)
                        and isinstance(sub.value, ast.Attribute)
                        and isinstance(sub.value.value, ast.Name)
                        and sub.value.value.id == "self"
                        and sub.value.attr in wrapped_attrs
                    ):
                        delegates = True
                        break
                if delegates:
                    break

        has_getattr_forwarding = any(m.name == "__getattr__" for m in methods) and bool(
            wrapped_attrs
        )

        if wrapped_attrs and (delegates or has_getattr_forwarding):
            is_proxy = any(
                "proxy" in w or "subject" in w or "target" in w for w in wrapped_attrs
            ) or "proxy" in node.name.lower()

            pattern_id = "proxy" if is_proxy else "decorator"
            pattern_name = "Proxy" if is_proxy else "Decorator"
            evidence = (
                f"Class '{node.name}' wraps and controls access to inner target"
                if is_proxy
                else f"Class '{node.name}' decorates and delegates calls to inner component"
            )

            self.patterns.append(
                PatternMatch(
                    pattern_id=pattern_id,
                    pattern_name=pattern_name,
                    category="structural",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=evidence,
                    confidence="high",
                )
            )

    def _check_observer_pattern(
        self, node: ast.ClassDef, method_names: set[str]
    ) -> None:
        has_subscribe = bool(
            method_names
            & {
                "subscribe",
                "attach",
                "register",
                "add_observer",
                "register_observer",
                "add_listener",
            }
        )
        has_notify = bool(
            method_names
            & {
                "notify",
                "notify_observers",
                "publish",
                "emit",
                "dispatch",
            }
        )

        if has_subscribe and has_notify:
            self.patterns.append(
                PatternMatch(
                    pattern_id="observer",
                    pattern_name="Observer",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' implements Observer pattern with registration and notification methods",
                    confidence="high",
                )
            )

    def _check_template_method_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        abstract_methods: set[str] = set()
        for m in methods:
            is_abstract = False
            for dec in m.decorator_list:
                if (isinstance(dec, ast.Name) and dec.id == "abstractmethod") or (
                    isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod"
                ):
                    is_abstract = True
                    break

            if len(m.body) == 1 and isinstance(m.body[0], ast.Raise):
                exc = m.body[0].exc
                if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                    is_abstract = True
                elif isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                    is_abstract = True

            if is_abstract:
                abstract_methods.add(m.name)

        has_template_call = False
        template_method_name = ""
        if abstract_methods:
            for m in methods:
                if m.name in abstract_methods or m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if (
                        isinstance(sub, ast.Call)
                        and isinstance(sub.func, ast.Attribute)
                        and isinstance(sub.func.value, ast.Name)
                        and sub.func.value.id == "self"
                        and sub.func.attr in abstract_methods
                    ):
                        has_template_call = True
                        template_method_name = m.name
                        break
                if has_template_call:
                    break

        if has_template_call:
            self.patterns.append(
                PatternMatch(
                    pattern_id="template_method",
                    pattern_name="Template Method",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' defines template method '{template_method_name}' coordinating abstract/hook methods",
                    confidence="high",
                )
            )

    def _check_strategy_pattern(
        self, node: ast.ClassDef, methods: list[ast.FunctionDef | ast.AsyncFunctionDef]
    ) -> None:
        strategy_param_found = False
        init_methods = [m for m in methods if m.name == "__init__"]
        if init_methods:
            init_m = init_methods[0]
            for arg in init_m.args.args + init_m.args.kwonlyargs:
                if arg.arg in ("self", "cls"):
                    continue
                if "strategy" in arg.arg.lower() or "algorithm" in arg.arg.lower():
                    strategy_param_found = True
                    break
                if arg.annotation:
                    try:
                        ann_str = ast.unparse(arg.annotation)
                        if "Callable" in ann_str or "Strategy" in ann_str:
                            strategy_param_found = True
                            break
                    except Exception:
                        pass

        has_strategy_delegation = False
        if strategy_param_found:
            for m in methods:
                if m.name.startswith("__"):
                    continue
                for sub in ast.walk(m):
                    if isinstance(sub, ast.Call):
                        if (
                            isinstance(sub.func, ast.Attribute)
                            and isinstance(sub.func.value, ast.Name)
                            and sub.func.value.id == "self"
                            and any(s in sub.func.attr.lower() for s in ("strategy", "algorithm"))
                        ):
                            has_strategy_delegation = True
                            break
                        if (
                            isinstance(sub.func, ast.Attribute)
                            and isinstance(sub.func.value, ast.Attribute)
                            and isinstance(sub.func.value.value, ast.Name)
                            and sub.func.value.value.id == "self"
                            and any(s in sub.func.value.attr.lower() for s in ("strategy", "algorithm"))
                        ):
                            has_strategy_delegation = True
                            break
                if has_strategy_delegation:
                    break

        name_lower = node.name.lower()
        if strategy_param_found and (
            has_strategy_delegation
            or "strategy" in name_lower
            or "context" in name_lower
        ):
            self.patterns.append(
                PatternMatch(
                    pattern_id="strategy",
                    pattern_name="Strategy",
                    category="behavioral",
                    file_path=self.file_path,
                    line_number=node.lineno,
                    evidence=f"Class '{node.name}' uses Strategy pattern accepting interchangeable Callable or algorithm",
                    confidence="high",
                )
            )


class CodebaseAnalyzer:
    """AST analyzer that detects design patterns and anti-patterns."""

    def analyze_source(
        self, source: str, file_path: str = "<memory>"
    ) -> tuple[list[PatternMatch], list[CodeSmell]]:
        """Parse source code string and detect patterns and code smells.

        Raises SyntaxError if source has invalid syntax.
        """
        tree = ast.parse(source, filename=file_path)
        visitor = _ASTAnalyzerVisitor(file_path=file_path)
        visitor.visit(tree)
        return visitor.patterns, visitor.smells

    def analyze_path(self, path: Path | str) -> AnalysisReport:
        """Analyze a file or directory recursively and return an AnalysisReport.

        Ignores hidden directories/files (starting with .) and __pycache__.
        Recovers gracefully from SyntaxError and UnicodeDecodeError.
        Raises FileNotFoundError if path does not exist.
        """
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        report = AnalysisReport(files_scanned=0, total_lines=0)

        if target.is_file():
            self._scan_file(target, report)
            return report

        for root, dirs, files in os.walk(target):
            # Exclude hidden directories and __pycache__ in-place
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d != "__pycache__"
            ]

            for file_name in sorted(files):
                if file_name.startswith(".") or not file_name.endswith(".py"):
                    continue

                file_path = Path(root) / file_name
                self._scan_file(file_path, report)

        return report

    def _scan_file(self, file_path: Path, report: AnalysisReport) -> None:
        try:
            source = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            report.syntax_errors.append(f"{file_path}: {e}")
            return

        lines = len(source.splitlines())
        report.total_lines += lines
        report.files_scanned += 1

        try:
            patterns, smells = self.analyze_source(source, file_path=str(file_path))
            report.detected_patterns.extend(patterns)
            report.code_smells.extend(smells)
        except SyntaxError as e:
            report.syntax_errors.append(f"{file_path}: {e}")
