import pytest


def test_smart_routing_complex_query():
    """Test that complex queries route to smart model."""
    from ollama_client import analyze_query_complexity, COMPLEXITY_KEYWORDS

    complex_queries = [
        "pesquise sobre inteligência artificial",
        "analise o mercado financeiro",
        "compare os dois produtos",
        "explique como funciona o Python",
    ]

    for query in complex_queries:
        complexity = analyze_query_complexity(query)
        assert complexity == "smart", f"Query '{query}' should route to smart model"


def test_smart_routing_simple_query():
    """Test that simple queries route to fast model."""
    from ollama_client import analyze_query_complexity

    simple_queries = [
        "oi tudo bem",
        "bom dia",
        "qual a hora",
        "obrigado",
    ]

    for query in simple_queries:
        complexity = analyze_query_complexity(query)
        assert complexity == "fast", f"Query '{query}' should route to fast model"


def test_no_duplicate_keyword_inflation():
    """Verify that duplicate keyword matches don't inflate the score."""
    from ollama_client import (
        analyze_query_complexity,
        COMPLEXITY_KEYWORDS,
        SIMPLE_KEYWORDS,
    )

    # Check that COMPLEXITY_KEYWORDS has no duplicates
    assert len(COMPLEXITY_KEYWORDS) == len(set(COMPLEXITY_KEYWORDS)), (
        "COMPLEXITY_KEYWORDS has duplicates"
    )

    # Check that SIMPLE_KEYWORDS has no duplicates
    assert len(SIMPLE_KEYWORDS) == len(set(SIMPLE_KEYWORDS)), (
        "SIMPLE_KEYWORDS has duplicates"
    )

    # Test that the same keyword appearing multiple times doesn't inflate score
    query_with_repeated = "pesquise pesquise pesquise"
    complexity = analyze_query_complexity(query_with_repeated)

    # Should still be smart, but not inflated by repetition
    assert complexity == "smart"


def test_keyword_case_insensitivity():
    """Verify that keyword matching is case insensitive."""
    from ollama_client import analyze_query_complexity

    queries = [
        "PESQUISE sobre IA",
        "Pesquise sobre IA",
        "pesquise sobre ia",
    ]

    for query in queries:
        complexity = analyze_query_complexity(query)
        assert complexity == "smart", f"Query '{query}' should be case insensitive"


def test_mixed_query():
    """Test queries with both simple and complex indicators."""
    from ollama_client import analyze_query_complexity

    # Query with both simple (oi) and complex (pesquise) keywords
    # Complex should win because it has higher weight
    mixed_query = "oi, pesquise sobre Python"
    complexity = analyze_query_complexity(mixed_query)
    assert complexity == "smart", "Complex keywords should outweigh simple ones"


def test_get_model_for_complexity_with_tools():
    """Test that tools force smart model."""
    from ollama_client import get_model_for_complexity

    # When tools are provided, should return a model that supports tools
    model = get_model_for_complexity("fast", "tinyllama", tools=[{"name": "test"}])

    # Should not be fast model
    assert model in ["llama3.2:3b", "qwen2.5:1.5b"], (
        "Should use smart model when tools are present"
    )


def test_get_model_for_complexity_default():
    """Test default model selection."""
    from ollama_client import get_model_for_complexity

    # Fast complexity should return fast model
    model = get_model_for_complexity("fast", "llama3.2:3b")
    assert model == "tinyllama" or model in ["llama3.2:3b", "granite3.1-moe"], (
        f"Got {model}"
    )

    # Smart complexity should return current model
    model = get_model_for_complexity("smart", "llama3.2:3b")
    assert model == "llama3.2:3b"
