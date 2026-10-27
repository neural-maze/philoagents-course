from langchain_core.messages import HumanMessage

from philoagents.domain.prompts import get_philosopher_prompt

PHILOSOPHER_VARS = {
    "philosopher_name": "苏格拉底",
    "philosopher_perspective": "不断追问 AI 的伦理基础",
    "philosopher_style": "友好、谦逊、好奇",
    "summary": "",
}


def test_philosopher_prompt_keeps_the_player_message():
    messages = get_philosopher_prompt().format_messages(
        messages=[HumanMessage(content="什么是真理？")],
        **PHILOSOPHER_VARS,
    )

    human = [m for m in messages if m.type == "human"]

    assert len(human) == 1
    assert human[0].content == "什么是真理？"


def test_philosopher_prompt_renders_character_card_and_language_rule():
    system = (
        get_philosopher_prompt()
        .format_messages(
            messages=[HumanMessage(content="什么是真理？")],
            **PHILOSOPHER_VARS,
        )[0]
        .content
    )

    assert "苏格拉底" in system
    assert "不断追问 AI 的伦理基础" in system
    assert "Reply in the language of the user's latest message" in system


def test_philosopher_prompt_does_not_leak_template_placeholders():
    system = (
        get_philosopher_prompt()
        .format_messages(
            messages=[HumanMessage(content="hi")],
            **PHILOSOPHER_VARS,
        )[0]
        .content
    )

    assert "{{" not in system
