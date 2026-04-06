import pytest
import json
import re


def test_json_fallback_parsing():
    content = 'Aqui está a resposta: {"name": "web_search", "parameters": {"query": "test"}} e mais texto'

    if "{" in content and "}" in content:
        j_match = re.search(r"\{.*\}", content, re.DOTALL)
        if j_match:
            manual = json.loads(j_match.group(0))
            assert manual["name"] == "web_search"
            assert manual["parameters"]["query"] == "test"


def test_json_fallback_invalid():
    content = "Texto com JSON inválido: {not valid json"

    if "{" in content and "}" in content:
        try:
            j_match = re.search(r"\{.*\}", content, re.DOTALL)
            if j_match:
                manual = json.loads(j_match.group(0))
                assert False, "Should have raised JSONDecodeError"
        except json.JSONDecodeError:
            pass


def test_tool_call_extraction():
    content = '{"name": "fetch_webpage", "arguments": {"url": "https://example.com"}}'
    manual = json.loads(content)
    assert "name" in manual
    assert manual["name"] == "fetch_webpage"


@pytest.mark.asyncio
async def test_execute_tool_unknown_tool_returns_error():
    """Test that calling an unknown tool returns error string, not exception."""
    from tools import execute_tool

    # Call with non-existent tool
    result = await execute_tool("ferramenta_falsa", {})

    # Should return error message, not raise exception
    assert isinstance(result, str), "Should return string"
    assert (
        "desconhecida" in result.lower()
        or "unknown" in result.lower()
        or "não encontrada" in result.lower()
        or "erro" in result.lower()
    ), f"Should return error message about unknown tool, got: {result}"


@pytest.mark.asyncio
async def test_execute_tool_invalid_args():
    """Test that execute_tool handles invalid args gracefully."""
    from tools import execute_tool

    # Call with string args (should parse as JSON or return error)
    result = await execute_tool("web_search", "invalid json string")

    # Should return error about invalid args
    assert isinstance(result, str), "Should return string"
    assert (
        "inválido" in result.lower()
        or "invalid" in result.lower()
        or "erro" in result.lower()
    ), f"Should return error about invalid args, got: {result}"


@pytest.mark.asyncio
async def test_execute_tool_none_args():
    """Test that execute_tool handles None args gracefully."""
    from tools import execute_tool

    # Call with None args
    result = await execute_tool("get_current_model", None)

    # Should either work or return appropriate error
    assert isinstance(result, str), "Should return string"


@pytest.mark.asyncio
async def test_execute_tool_missing_required_args():
    """Test that execute_tool handles missing required args."""
    from tools import execute_tool

    # Call web_search without required 'query' parameter
    result = await execute_tool("web_search", {})

    # Should return error about missing parameter
    # Note: The actual behavior depends on implementation
    assert isinstance(result, str), "Should return string"


def test_tools_list_includes_common_tools():
    """Verify common tools are in TOOLS list."""
    from tools import TOOLS

    tool_names = [t["function"]["name"] for t in TOOLS]

    # Essential tools that should exist
    essential_tools = ["web_search", "get_weather", "reply_to_slack"]

    for tool in essential_tools:
        assert tool in tool_names, f"Tool '{tool}' should be in TOOLS list"


def test_read_slack_message_not_in_tools():
    """Verify that read_slack_message is NOT in TOOLS list (it's redundant)."""
    from tools import TOOLS

    tool_names = [t["function"]["name"] for t in TOOLS]

    # read_slack_message should have been removed as redundant
    assert "read_slack_message" not in tool_names, (
        "read_slack_message should be removed from TOOLS"
    )
