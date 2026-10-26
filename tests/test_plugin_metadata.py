import json
from pathlib import Path


def test_plugin_json_valid():
    manifest_path = Path("plugin.json")
    assert manifest_path.exists(), "plugin.json should exist"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data.get("name") == "design-patterns"
    assert "description" in data
    assert "version" in data
    assert "suggestedPrompts" in data
    assert isinstance(data["suggestedPrompts"], list)
    assert len(data["suggestedPrompts"]) >= 2


def test_skill_md_valid():
    skill_path = Path("skills/design-patterns/SKILL.md")
    assert skill_path.exists(), "skills/design-patterns/SKILL.md should exist"
    content = skill_path.read_text(encoding="utf-8")
    assert content.startswith("---")
    assert "name: design-patterns" in content
    assert "description:" in content
    assert "bin/pat recommend" in content
    assert "bin/pat show" in content
    assert "bin/pat scaffold" in content
    assert "bin/pat analyze" in content or "pat analyze" in content
    assert "bin/pat matrix" in content or "pat matrix" in content
    assert "--py" in content
    assert "YAGNI" in content or "KISS" in content


def test_rules_agents_md_valid():
    rule_path = Path("rules/AGENTS.md")
    assert rule_path.exists(), "rules/AGENTS.md should exist"
    content = rule_path.read_text(encoding="utf-8")
    assert "Design Patterns" in content
    assert "SOLID" in content
    assert "Coupling" in content or "coupling" in content
    assert "Cohesion" in content or "cohesion" in content
    assert "YAGNI" in content or "KISS" in content
    assert "Pythonic-First" in content
    assert "Stop Writing Classes" in content or "stop writing classes" in content.lower()
    assert "classic" in content.lower()
    assert "3.10" in content
    assert "3.12" in content
    assert "pat analyze" in content
    assert "Requires Python" in content


def test_readme_md_valid():
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md should exist"
    content = readme_path.read_text(encoding="utf-8")
    assert "agy plugin install" in content
    assert "pip install ." in content
    assert "bin/pat" in content or "pat" in content
    assert "Architecture" in content or "architecture" in content
    for cmd in [
        "list",
        "show",
        "search",
        "recommend",
        "scaffold",
        "diagnose",
        "analyze",
        "matrix",
    ]:
        assert cmd in content
    assert "--py" in content


def test_version_synchronization():
    import design_patterns
    manifest = json.loads(Path("plugin.json").read_text(encoding="utf-8"))
    assert design_patterns.__version__ == "0.1.0"
    assert manifest["version"] == "0.1.0"
