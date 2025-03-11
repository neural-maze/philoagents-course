from langchain.tools.retriever import create_retriever_tool

from philoagents.application.rag.retrievers import get_retriever
from philoagents.config import settings

retriever = get_retriever(
    embedding_model_id=settings.RAG_TEXT_EMBEDDING_MODEL_ID,
    k=settings.RAG_TOP_K,
    device=settings.RAG_DEVICE)

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_philosopher_context",
    "Search and return information about a specific philosopher. Always use this tool when the user asks you about a philosopher, their works, ideas or historical context.",
)

tools = [retriever_tool]