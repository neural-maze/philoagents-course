from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_groq import ChatGroq

from philoagents.domain.prompts import (
    EXTEND_SUMMARY_PROMPT,
    PHILOSOPHER_CHARACTER_CARD,
    SUMMARY_PROMPT,
)
from philoagents.config import settings


def get_chat_model(temperature: float = 0.7) -> ChatGroq:
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_LLM_MODEL,
        temperature=temperature,
    )


def get_philosopher_response_chain():
    model = get_chat_model()
    system_message = PHILOSOPHER_CHARACTER_CARD

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message.prompt),
            MessagesPlaceholder(variable_name="messages"),
        ],
        template_format="jinja2",
    )

    return prompt | model


def get_summary_chain(summary: str = ""):
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
