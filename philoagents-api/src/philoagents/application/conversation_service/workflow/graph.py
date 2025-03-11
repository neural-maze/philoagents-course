from functools import lru_cache

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from philoagents.application.conversation_service.workflow.edges import (
    should_summarize_conversation,
)
from philoagents.application.conversation_service.workflow.nodes import (
    conversation_node,
    summarize_conversation_node,
    retriever_node,
)
from philoagents.application.conversation_service.workflow.state import PhilosopherState


@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(PhilosopherState)

    # Add all nodes
    graph_builder.add_node("conversation_node", conversation_node)
    graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)
    graph_builder.add_node("retrieve", retriever_node)
    
    # Define the flow
    graph_builder.add_conditional_edges(
        START, should_summarize_conversation
    )
    graph_builder.add_edge("summarize_conversation_node", "conversation_node")
    
    graph_builder.add_conditional_edges(
        "conversation_node",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        }
    )
    graph_builder.add_edge("retrieve", "conversation_node")

    return graph_builder
