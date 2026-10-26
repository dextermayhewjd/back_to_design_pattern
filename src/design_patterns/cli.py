"""Command line interface for Design Patterns."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from design_patterns.catalog import load_default_registry
from design_patterns.models import Category, Pattern
from design_patterns.recommender import PatternRecommender
from design_patterns.registry import PatternRegistry


def _pattern_not_found_error(pattern_id: str, registry: PatternRegistry) -> str:
    all_ids = [p.id for p in registry.list_all()]
    matches = difflib.get_close_matches(pattern_id, all_ids, n=3, cutoff=0.6)
    msg = f"Error: Pattern '{pattern_id}' not found.\n"
    if matches:
        msg += f"Did you mean: {', '.join(matches)}?\n"
    msg += "Run 'pat list' to see all available patterns.\n"
    return msg


def _detect_runtime_version() -> str:
    """Auto-detect the best Python version tier matching the current runtime."""
    if sys.version_info >= (3, 12):
        return "3.12"
    elif sys.version_info >= (3, 10):
        return "3.10"
    return "classic"


def _resolve_version(py: str = "auto", type_arg: str | None = None) -> str:
    """Resolve Python version tier with auto-detection and backward-compatible --type flags."""
    detected = _detect_runtime_version()
    if py and py != "auto":
        return py
    if type_arg:
        if type_arg in ("conceptual", "classic-oop"):
            return "classic"
        elif type_arg in ("realworld", "pythonic"):
            return detected
    return detected


def _format_version_badge(pattern: Pattern, py_version: str = "3.10") -> str:
    """Format explicit version baseline badge for recommendation results."""
    target = py_version if py_version != "auto" else "3.10"
    evo = pattern.get_evolution(target)
    if evo.key_features:
        features_str = " / ".join(evo.key_features[:3])
        return f"[Best Practice: Python {evo.version_tag} ({features_str})]"
    return f"[Requires Python {evo.version_tag}]"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pat",
        description="Python Design Patterns CLI - RefactoringGuru-faithful patterns, recommender, and code generator.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # list
    list_p = subparsers.add_parser("list", help="List design patterns")
    list_p.add_argument(
        "--category", "-c",
        choices=["creational", "structural", "behavioral"],
        help="Filter by category",
    )
    list_p.add_argument("--json", action="store_true", help="Output as JSON")

    # show
    show_p = subparsers.add_parser("show", help="Show pattern details")
    show_p.add_argument("pattern", help="Pattern identifier (e.g. abstract-factory, strategy)")
    show_p.add_argument("--summary", action="store_true", help="Display a concise summary")
    show_p.add_argument("--json", action="store_true", help="Output as JSON")

    # code
    code_p = subparsers.add_parser("code", help="Print Python implementation code")
    code_p.add_argument("pattern", help="Pattern identifier")
    code_p.add_argument(
        "--py",
        choices=["auto", "classic", "3.10", "3.12"],
        default="auto",
        help="Python version target tier (default: auto)",
    )
    code_p.add_argument(
        "--type", "-t",
        choices=["pythonic", "realworld", "conceptual", "classic-oop"],
        default=None,
        help="Legacy code variant (backward-compatible, maps to --py)",
    )
    code_p.add_argument("--json", action="store_true", help="Output code as JSON")

    # scaffold
    scaffold_p = subparsers.add_parser("scaffold", help="Generate boilerplate template")
    scaffold_p.add_argument("pattern", help="Pattern identifier")
    scaffold_p.add_argument("--out", "-o", help="Target output file path")
    scaffold_p.add_argument(
        "--overwrite", "--force",
        dest="overwrite",
        action="store_true",
        help="Overwrite existing destination file",
    )
    scaffold_p.add_argument("--json", action="store_true", help="Output scaffold template as JSON")

    # recommend
    rec_p = subparsers.add_parser("recommend", help="Recommend design patterns based on problem query")
    rec_p.add_argument("--query", "-q", help="Problem description or design symptom")
    rec_p.add_argument("--interactive", "-i", action="store_true", help="Launch interactive diagnostic wizard")
    rec_p.add_argument(
        "--py",
        choices=["auto", "classic", "3.10", "3.12"],
        default="auto",
        help="Python version target tier for badges (default: auto)",
    )
    rec_p.add_argument("--top", type=int, default=3, help="Max recommendations to return (default: 3)")
    rec_p.add_argument("--json", action="store_true", help="Output recommendations as JSON")

    # search (alias to recommend --query)
    search_p = subparsers.add_parser("search", help="Search patterns by problem description or keywords")
    search_p.add_argument("query", help="Problem description or search keyword")
    search_p.add_argument(
        "--py",
        choices=["auto", "classic", "3.10", "3.12"],
        default="auto",
        help="Python version target tier for badges (default: auto)",
    )
    search_p.add_argument("--top", type=int, default=3, help="Max recommendations to return (default: 3)")
    search_p.add_argument("--json", action="store_true", help="Output recommendations as JSON")
    search_p.set_defaults(interactive=False)

    # diagnose (alias to recommend --interactive)
    diagnose_p = subparsers.add_parser("diagnose", help="Launch interactive diagnostic wizard")
    diagnose_p.add_argument(
        "--py",
        choices=["auto", "classic", "3.10", "3.12"],
        default="auto",
        help="Python version target tier for badges (default: auto)",
    )
    diagnose_p.add_argument("--json", action="store_true", help="Output recommendations as JSON")
    diagnose_p.set_defaults(interactive=True, query=None, top=3)

    # run
    run_p = subparsers.add_parser("run", help="Execute runnable pattern example")
    run_p.add_argument("pattern", help="Pattern identifier")
    run_p.add_argument(
        "--py",
        choices=["auto", "classic", "3.10", "3.12"],
        default="auto",
        help="Python version target tier (default: auto)",
    )
    run_p.add_argument(
        "--type", "-t",
        choices=["pythonic", "realworld", "conceptual", "classic-oop"],
        default=None,
        help="Legacy example variant to run (default: auto)",
    )

    # matrix
    matrix_p = subparsers.add_parser("matrix", help="Display 3-tier version evolution matrix")
    matrix_p.add_argument("pattern", help="Pattern identifier (e.g. strategy, factory-method)")
    matrix_p.add_argument("--json", action="store_true", help="Output evolution matrix as JSON")

    # analyze
    analyze_p = subparsers.add_parser("analyze", help="Analyze codebase for design patterns and code smells")
    analyze_p.add_argument("target_path", help="Path to file or directory to analyze")
    analyze_p.add_argument("--json", action="store_true", help="Output analysis report as JSON")

    return parser


def handle_list(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    category = Category(args.category) if args.category else None
    patterns = registry.list_all(category)

    if args.json:
        data = [
            {
                "id": p.id,
                "name": p.name,
                "chinese_name": p.chinese_name,
                "category": p.category.value,
                "intent": p.intent,
            }
            for p in patterns
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(f"\n{'=' * 75}")
    print(f"{'ID':<26} {'NAME (中文)':<24} {'CATEGORY':<14}")
    print(f"{'=' * 75}")
    for p in patterns:
        display_name = f"{p.name} ({p.chinese_name})"
        print(f"{p.id:<26} {display_name:<24} {p.category.value:<14}")
        print(f"  └─ {p.intent}")
    print(f"{'=' * 75}")
    print(f"Total: {len(patterns)} patterns\n")
    return 0


def handle_show(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    evo_classic = pattern.get_evolution("classic")
    evo_310 = pattern.get_evolution("3.10")
    evo_312 = pattern.get_evolution("3.12")

    evolution_dict = {
        "classic": evo_classic.summary,
        "3.10+": evo_310.summary,
        "3.12+": evo_312.summary,
    }

    if getattr(args, "summary", False):
        if args.json:
            data = {
                "id": pattern.id,
                "name": pattern.name,
                "chinese_name": pattern.chinese_name,
                "category": pattern.category.value,
                "intent": pattern.intent,
                "evolution": evolution_dict,
            }
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return 0
        print(f"\n# {pattern.name} / {pattern.chinese_name} [{pattern.category.value.upper()}]")
        print(f"\n## 意图 (Intent)\n{pattern.intent}")
        print("\n## 版本演进 (Version Evolution):")
        print(f"  • Classic GoF: {evo_classic.summary}")
        print(f"  • Python 3.10+: {evo_310.summary}")
        print(f"  • Python 3.12+: {evo_312.summary}\n")
        return 0

    if args.json:
        data = {
            "id": pattern.id,
            "name": pattern.name,
            "chinese_name": pattern.chinese_name,
            "category": pattern.category.value,
            "intent": pattern.intent,
            "problem": pattern.problem,
            "solution": pattern.solution,
            "applicability": pattern.applicability,
            "symptoms": pattern.symptoms,
            "pros": pattern.pros,
            "cons": pattern.cons,
            "relations": pattern.relations,
            "evolution": evolution_dict,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(f"\n# {pattern.name} / {pattern.chinese_name} [{pattern.category.value.upper()}]")
    print(f"\n## 意图 (Intent)\n{pattern.intent}")
    print(f"\n## 问题 (Problem)\n{pattern.problem}")
    print(f"\n## 解决方案 (Solution)\n{pattern.solution}")
    print("\n## 版本演进 (Version Evolution):")
    print(f"  • Classic GoF: {evo_classic.summary}")
    print(f"  • Python 3.10+: {evo_310.summary}")
    print(f"  • Python 3.12+: {evo_312.summary}")
    print("\n## 适合应用场景 (Applicability):")
    for app in pattern.applicability:
        print(f"  • {app}")
    print("\n## 优缺点 (Pros & Cons):")
    print("  [优点]")
    for pro in pattern.pros:
        print(f"    ✔ {pro}")
    print("  [缺点]")
    for con in pattern.cons:
        print(f"    ✖ {con}")
    print("\n## 与其他模式的关系 (Relations):")
    for rel in pattern.relations:
        print(f"  → {rel}")
    print("")
    return 0


def handle_code(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    version = _resolve_version(getattr(args, "py", "auto"), getattr(args, "type", None))
    code = pattern.get_evolution(version).code

    if getattr(args, "json", False):
        data = {
            "id": pattern.id,
            "name": pattern.name,
            "py": version,
            "type": args.type if args.type is not None else version,
            "code": code,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(code)
    return 0


def handle_scaffold(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    template = pattern.scaffold_template
    if not args.out:
        if getattr(args, "json", False):
            data = {
                "id": pattern.id,
                "name": pattern.name,
                "scaffold_template": template,
            }
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return 0
        print(template)
        return 0

    target = Path(args.out)
    if target.is_dir():
        sys.stderr.write(f"Error: Target path '{args.out}' is a directory, not a file.\n")
        return 1
    if target.exists() and not args.overwrite:
        sys.stderr.write(f"Error: Target file '{args.out}' already exists. Use --overwrite to replace it.\n")
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template, encoding="utf-8")
    print(f"Successfully generated scaffold for {pattern.name} at: {args.out}")
    return 0


def handle_recommend(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    recommender = PatternRecommender(registry)
    py_version = getattr(args, "py", "auto")

    if getattr(args, "interactive", False):
        try:
            results = recommender.run_interactive_wizard()
        except (KeyboardInterrupt, EOFError):
            print("\nDiagnostic cancelled.")
            return 0
    elif getattr(args, "query", None) is not None:
        if not args.query.strip():
            sys.stderr.write("Error: Please provide a query describing your design problem.\n")
            return 1
        results = recommender.recommend(args.query, top_k=getattr(args, "top", 3))
    else:
        sys.stderr.write("Error: Specify a query with -q/--query or run --interactive.\n")
        return 1

    if getattr(args, "json", False):
        data = [
            {
                "id": r.pattern.id,
                "name": r.pattern.name,
                "chinese_name": r.pattern.chinese_name,
                "category": r.pattern.category.value,
                "score": round(r.score, 2),
                "rationale": r.rationale,
                "intent": r.pattern.intent,
                "version_badge": _format_version_badge(r.pattern, py_version),
            }
            for r in results
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    if not results:
        print("\nNo matching design pattern found with high confidence.")
        print("Try rephrasing your problem or run 'pat list' to browse all 22 patterns.\n")
        return 0

    print(f"\n{'=' * 75}")
    print("RECOMMENDED DESIGN PATTERNS")
    print(f"{'=' * 75}")
    for idx, r in enumerate(results, 1):
        p = r.pattern
        badge = _format_version_badge(p, py_version)
        print(f"[{idx}] {p.name} ({p.chinese_name}) [{p.category.value}] (Score: {r.score:.1f}) {badge}")
        print(f"    Intent: {p.intent}")
        print(f"    Rationale: {r.rationale}")
        print(f"    Best Practice: {badge}")
        print(f"    Quick view: pat show {p.id}")
        print(f"    Scaffold:   pat scaffold {p.id} --out my_module.py")
        print("-" * 75)
    print("")
    return 0


def handle_run(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    py_choice = getattr(args, "py", "auto")
    type_choice = getattr(args, "type", None)
    version = _resolve_version(py_choice, type_choice)

    if version == "3.12" and sys.version_info < (3, 12):
        sys.stderr.write(
            f"Error: Python 3.12+ is required to execute PEP 695 syntax (current: {sys.version.split()[0]}).\n"
        )
        return 1

    code = pattern.get_evolution(version).code
    display_type = type_choice if type_choice else version
    print(f"--- Running {pattern.name} ({display_type}) ---")
    exec_scope: dict = {"__name__": "__main__"}
    try:
        exec(code, exec_scope)
    except Exception as e:
        sys.stderr.write(f"Execution error: {e}\n")
        return 1
    return 0


def handle_matrix(args: argparse.Namespace) -> int:
    registry = load_default_registry()
    pattern = registry.get(args.pattern)
    if not pattern:
        sys.stderr.write(_pattern_not_found_error(args.pattern, registry))
        return 1

    evo_classic = pattern.get_evolution("classic")
    evo_310 = pattern.get_evolution("3.10")
    evo_312 = pattern.get_evolution("3.12")

    if getattr(args, "json", False):
        data = {
            "id": pattern.id,
            "name": pattern.name,
            "chinese_name": pattern.chinese_name,
            "tiers": [
                {
                    "tier": evo_classic.version_tag,
                    "lines": evo_classic.line_count,
                    "key_features": evo_classic.key_features,
                    "summary": evo_classic.summary,
                    "notes": pattern.matrix_notes.get("classic", ""),
                    "code": evo_classic.code,
                },
                {
                    "tier": evo_310.version_tag,
                    "lines": evo_310.line_count,
                    "key_features": evo_310.key_features,
                    "summary": evo_310.summary,
                    "notes": pattern.matrix_notes.get("3.10", ""),
                    "code": evo_310.code,
                },
                {
                    "tier": evo_312.version_tag,
                    "lines": evo_312.line_count,
                    "key_features": evo_312.key_features,
                    "summary": evo_312.summary,
                    "notes": pattern.matrix_notes.get("3.12", ""),
                    "code": evo_312.code,
                },
            ],
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(f"\nEvolution Matrix: {pattern.name} ({pattern.id})")
    print(f"{'=' * 85}")
    print(f"{'Tier':<10} {'Lines':<8} {'Key Features':<32} {'Summary'}")
    print(f"{'-' * 85}")
    for evo in (evo_classic, evo_310, evo_312):
        feat = ", ".join(evo.key_features)
        print(f"{evo.version_tag:<10} {evo.line_count:<8} {feat:<32} {evo.summary}")
    print(f"{'=' * 85}")

    print("\nEvolution Notes:")
    for key, tag in [("classic", "classic"), ("3.10", "3.10+"), ("3.12", "3.12+")]:
        note = pattern.matrix_notes.get(key, "").strip()
        print(f"\n[{tag}]")
        if note:
            print(f"  {note}")
        else:
            print("  (No specific evolution notes)")
    print("")
    return 0


def handle_analyze(args: argparse.Namespace) -> int:
    target_path = Path(args.target_path)
    if not target_path.exists():
        sys.stderr.write(f"Error: Target path '{args.target_path}' does not exist.\n")
        return 1

    from design_patterns.analyzer import CodebaseAnalyzer

    analyzer = CodebaseAnalyzer()
    try:
        report = analyzer.analyze_path(target_path)
    except FileNotFoundError:
        sys.stderr.write(f"Error: Target path '{args.target_path}' does not exist.\n")
        return 1

    if getattr(args, "json", False):
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return 0

    print(f"\nScanned {report.files_scanned} files ({report.total_lines} lines)")
    print(f"{'=' * 75}")

    if report.detected_patterns:
        print("\nDetected Patterns:")
        for p in report.detected_patterns:
            print(f"  [{p.pattern_id}] {p.file_path}:{p.line_number} - {p.evidence}")

    if report.code_smells:
        print("\nCode Smells:")
        for s in report.code_smells:
            print(f"  [{s.smell_type}] {s.file_path}:{s.line_number}")
            print(f"    Description: {s.description}")
            print(f"    Recommended Pattern: {s.recommended_pattern}")
            print(f"    Version Baseline: [Requires {s.target_version_baseline}]")
            print(f"    Refactoring Tip: {s.refactoring_tip}")

    if report.syntax_errors:
        print("\nSyntax Errors:")
        for err in report.syntax_errors:
            print(f"  • {err}")

    if not report.detected_patterns and not report.code_smells and not report.syntax_errors:
        print("\nNo design patterns or code smells detected.")

    print("")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    handlers = {
        "list": handle_list,
        "show": handle_show,
        "code": handle_code,
        "scaffold": handle_scaffold,
        "recommend": handle_recommend,
        "search": handle_recommend,
        "diagnose": handle_recommend,
        "run": handle_run,
        "matrix": handle_matrix,
        "analyze": handle_analyze,
    }

    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return 1

    try:
        return handler(args)
    except (KeyboardInterrupt, EOFError):
        return 0


if __name__ == "__main__":
    sys.exit(main())
