from llm_poker.llm_player import parse_llm_json, ActionSchema


def test_parse_llm_json_with_reasoning_block():
    raw = (
        "<poker_reasoning>Some thoughts...</poker_reasoning>\n"
        "{\n  \"action\": \"call\",\n  \"raise_amount\": null\n}\n"
    )
    data = parse_llm_json(raw, ActionSchema)
    assert data.action == "call"
    assert data.raise_amount is None

