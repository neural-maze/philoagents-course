import uuid
from contextlib import AsyncExitStack
from typing import Any, AsyncGenerator, Union

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from loguru import logger
from opik.integrations.langchain import OpikTracer

from philoagents.application.conversation_service.workflow.graph import (
    create_workflow_graph,
)
from philoagents.application.conversation_service.workflow.state import PhilosopherState
from philoagents.config import settings
from philoagents.infrastructure.opik_utils import tracing_enabled

_stack: AsyncExitStack | None = None
_graph = None
_tracing_callbacks: list = []


async def get_compiled_graph():
    """Build the checkpointer and the compiled graph once per process.

    Both used to be created inside every request, which meant a fresh Mongo connection
    and a full graph compile per player message.
    """
    global _stack, _graph

    if _graph is not None:
        return _graph

    stack = AsyncExitStack()
    checkpointer = await stack.enter_async_context(
        AsyncMongoDBSaver.from_conn_string(
            conn_string=settings.MONGO_URI,
            db_name=settings.MONGO_DB_NAME,
            checkpoint_collection_name=settings.MONGO_STATE_CHECKPOINT_COLLECTION,
            writes_collection_name=settings.MONGO_STATE_WRITES_COLLECTION,
        )
    )

    graph = create_workflow_graph().compile(checkpointer=checkpointer)
    if tracing_enabled():
        _tracing_callbacks.append(OpikTracer(graph=graph.get_graph(xray=True)))

    _stack, _graph = stack, graph
    logger.info("Conversation workflow compiled and cached")
    return _graph


async def shutdown_workflow_graph() -> None:
    global _stack, _graph

    if _stack is not None:
        await _stack.aclose()
    _stack, _graph = None, None
    _tracing_callbacks.clear()


def _thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}, "callbacks": _tracing_callbacks}


async def get_response(
    messages: str | list[str] | list[dict[str, Any]],
    philosopher_id: str,
    philosopher_name: str,
    philosopher_perspective: str,
    philosopher_style: str,
    philosopher_context: str,
    new_thread: bool = False,
    player_id:str="local",
) -> tuple[str, PhilosopherState]:
    """Run a conversation through the workflow graph.

    Args:
        message: Initial message to start the conversation.
        philosopher_id: Unique identifier for the philosopher.
        philosopher_name: Name of the philosopher.
        philosopher_perspective: Philosopher's perspective on the topic.
        philosopher_style: Style of conversation (e.g., "Socratic").
        philosopher_context: Additional context about the philosopher.

    Returns:
        tuple[str, PhilosopherState]: A tuple containing:
            - The content of the last message in the conversation.
            - The final state after running the workflow.

    Raises:
        RuntimeError: If there's an error running the conversation workflow.
    """

    try:
        graph = await get_compiled_graph()

        output_state = await graph.ainvoke(
            input={
                "messages": __format_messages(messages=messages),
                "philosopher_name": philosopher_name,
                "philosopher_perspective": philosopher_perspective,
                "philosopher_style": philosopher_style,
                "philosopher_context": philosopher_context,
            },
            config=_thread_config(
                _thread_id(player_id, philosopher_id, new_thread)
            ),
        )

        last_message = output_state["messages"][-1]
        return last_message.content, PhilosopherState(**output_state)
    except Exception as e:
        raise RuntimeError(f"Error running conversation workflow: {str(e)}") from e


async def get_streaming_response(
    messages: str | list[str] | list[dict[str, Any]],
    philosopher_id: str,
    philosopher_name: str,
    philosopher_perspective: str,
    philosopher_style: str,
    philosopher_context: str,
    new_thread: bool = False,
    player_id:str="local",
) -> AsyncGenerator[str, None]:
    """Run a conversation through the workflow graph with streaming response.

    Args:
        messages: Initial message to start the conversation.
        philosopher_id: Unique identifier for the philosopher.
        philosopher_name: Name of the philosopher.
        philosopher_perspective: Philosopher's perspective on the topic.
        philosopher_style: Style of conversation (e.g., "Socratic").
        philosopher_context: Additional context about the philosopher.
        new_thread: Whether to create a new conversation thread.

    Yields:
        Chunks of the response as they become available.

    Raises:
        RuntimeError: If there's an error running the conversation workflow.
    """
    try:
        graph = await get_compiled_graph()

        async for chunk in graph.astream(
            input={
                "messages": __format_messages(messages=messages),
                "philosopher_name": philosopher_name,
                "philosopher_perspective": philosopher_perspective,
                "philosopher_style": philosopher_style,
                "philosopher_context": philosopher_context,
            },
            config=_thread_config(
                _thread_id(player_id, philosopher_id, new_thread)
            ),
            stream_mode="messages",
        ):
            if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(
                chunk[0], AIMessageChunk
            ):
                yield chunk[0].content

    except Exception as e:
        raise RuntimeError(
            f"Error running streaming conversation workflow: {str(e)}"
        ) from e


def _thread_id(player_id: str, philosopher_id: str, new_thread: bool) -> str:
    base_thread_id = f"{player_id}:{philosopher_id}"
    if not new_thread:
        return base_thread_id
    return f"{base_thread_id}:{uuid.uuid4()}"


def __format_messages(
    messages: Union[str, list[dict[str, Any]]],
) -> list[Union[HumanMessage, AIMessage]]:
    """Convert various message formats to a list of LangChain message objects.

    Args:
        messages: Can be one of:
            - A single string message
            - A list of string messages
            - A list of dictionaries with 'role' and 'content' keys

    Returns:
        List[Union[HumanMessage, AIMessage]]: A list of LangChain message objects
    """

    if isinstance(messages, str):
        return [HumanMessage(content=messages)]

    if isinstance(messages, list):
        if not messages:
            return []

        if (
            isinstance(messages[0], dict)
            and "role" in messages[0]
            and "content" in messages[0]
        ):
            result = []
            for msg in messages:
                if msg["role"] == "user":
                    result.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    result.append(AIMessage(content=msg["content"]))
            return result

        return [HumanMessage(content=message) for message in messages]

    return []
