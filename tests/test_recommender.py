from design_patterns.catalog import load_default_registry
from design_patterns.recommender import PatternRecommender, RecommendationResult

def test_recommend_by_symptoms_and_keywords():
    registry = load_default_registry()
    recommender = PatternRecommender(registry)
    
    results = recommender.recommend("I need to swap interchangeable algorithms at runtime")
    assert len(results) > 0
    assert results[0].pattern.id == "strategy"
    assert any("algorithm" in s.lower() or "runtime" in s.lower() for s in results[0].matched_symptoms)

    undo_results = recommender.recommend("need undo and redo history rollback")
    top_ids = [r.pattern.id for r in undo_results]
    assert "memento" in top_ids or "command" in top_ids

def test_recommend_empty_query():
    registry = load_default_registry()
    recommender = PatternRecommender(registry)
    results = recommender.recommend("")
    assert results == []

def test_interactive_wizard_flow():
    registry = load_default_registry()
    recommender = PatternRecommender(registry)
    
    # Simulate user answering:
    # 1. Category: 3 (Behavioral)
    # 2. Challenge: 1 (Encapsulate algorithm variants)
    # 3. Specific: 1 (Runtime interchangeable strategies)
    mock_inputs = iter(["3", "1", "1"])
    printed: list[str] = []
    
    results = recommender.run_interactive_wizard(
        input_fn=lambda _: next(mock_inputs),
        print_fn=lambda msg="": printed.append(str(msg))
    )
    assert len(results) > 0
    assert results[0].pattern.id == "strategy"


def test_recommend_unspaced_chinese_query():
    registry = load_default_registry()
    recommender = PatternRecommender(registry)

    results = recommender.recommend("我想用工厂方法")
    assert len(results) > 0
    assert results[0].pattern.id == "factory-method"

    results_af = recommender.recommend("需要抽象工厂")
    assert len(results_af) > 0
    assert results_af[0].pattern.id == "abstract-factory"
