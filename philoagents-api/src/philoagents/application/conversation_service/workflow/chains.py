from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from philoagents.application.conversation_service.workflow.tools import get_tools
from philoagents.config import settings
from philoagents.domain.prompts import (
    CONTEXT_SUMMARY_PROMPT,
    EXTEND_SUMMARY_PROMPT,
    SUMMARY_PROMPT,
    get_philosopher_prompt,
)


def get_chat_model(temperature: float = 0.7) -> ChatOpenAI:
    if not settings.QWEN_API_KEY:
        raise RuntimeError("QWEN_API_KEY is not set. The philosopher cannot answer.")

    return ChatOpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        model=settings.QWEN_MODEL,
        temperature=temperature,
        extra_body={"enable_thinking": False},
    )


def get_philosopher_response_chain():
    return get_philosopher_prompt() | get_chat_model().bind_tools(get_tools())


def get_conversation_summary_chain(summary: str = ""):
    model = get_chat_model()

    summary_message = EXTEND_SUMMARY_PROMPT if summary else SUMMARY_PROMPT

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            ("human", summary_message.prompt),
        ],
        template_format="jinja2",
    )

    return prompt | model


def get_context_summary_chain():
    model = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", CONTEXT_SUMMARY_PROMPT.prompt),
        ],
        template_format="jinja2",
    )

    return prompt | model
