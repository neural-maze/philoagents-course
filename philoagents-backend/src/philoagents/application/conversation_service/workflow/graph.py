from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from philoagents.application.conversation_service.workflow.edges import (
    should_summarize_conversation,
)
from philoagents.application.conversation_service.workflow.nodes import (
    conversation_node,
    summarize_conversation_node,
)
from philoagents.application.conversation_service.workflow.state import PhilosopherState


@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(PhilosopherState)

    # Add all nodes
    graph_builder.add_node("conversation_node", conversation_node)
    graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)

    # Define the flow
    graph_builder.add_edge(START, "conversation_node")

    # Check for summarization after any response
    graph_builder.add_conditional_edges(
        "conversation_node", should_summarize_conversation
    )
    graph_builder.add_edge("summarize_conversation_node", END)

    return graph_builder
