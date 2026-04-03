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
