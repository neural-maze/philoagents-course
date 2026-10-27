import re

from loguru import logger

from philoagents.config import settings
from philoagents.infrastructure.mongo.database import get_database


def reset_conversation_state(player_id: str) -> dict:
    """Delete one player's LangGraph conversation state.

    Scoped by the thread_id prefix on purpose: the old implementation dropped the whole
    collection, so any player pressing reset erased every other player's memory.

    Returns:
        dict: the player and how many documents each collection lost.
    """
    db = get_database()
    # player_id is client supplied, so anchor it and escape it before it reaches $regex.
    thread_filter = {"thread_id": {"$regex": f"^{re.escape(player_id)}:"}}

    deleted = {}
    for name in (
        settings.MONGO_STATE_CHECKPOINT_COLLECTION,
        settings.MONGO_STATE_WRITES_COLLECTION,
    ):
        count = db[name].delete_many(thread_filter).deleted_count
        deleted[name] = count
        logger.info(f"Reset player {player_id}: removed {count} documents from {name}")

    return {"status": "success", "player_id": player_id, "deleted": deleted}
