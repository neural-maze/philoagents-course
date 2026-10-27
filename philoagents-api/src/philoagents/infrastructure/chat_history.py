from datetime import datetime, timezone
from functools import lru_cache

from pymongo import ASCENDING

from philoagents.config import settings
from philoagents.infrastructure.mongo.database import get_database


@lru_cache(maxsize=1)
def _collection():
    return get_database()[settings.MONGO_CHAT_HISTORY_COLLECTION]


def ensure_indexes() -> None:
    """The history panel always reads one player's one NPC, newest first."""
    _collection().create_index(
        [
            ("player_id", ASCENDING),
            ("philosopher_id", ASCENDING),
            ("created_at", ASCENDING),
        ],
        name="player_philosopher_time",
    )


def save_turn(
        player_id: str,
        philosopher_id: str,
        user_message: str,
        assistant_message: str,
) -> None:
    """保存一轮完整的玩家与 NPC 对话。"""

    document = {
        "player_id": player_id,
        "philosopher_id": philosopher_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "created_at": datetime.now(timezone.utc),
    }

    _collection().insert_one(document)


def get_turns(
        player_id: str,
        philosopher_id: str,
        limit: int = 100,
) -> list[dict]:
    """查询某位玩家与某位 NPC 最近的聊天记录。"""

    documents = list(
        _collection()
        .find(
            {
                "player_id": player_id,
                "philosopher_id": philosopher_id,
            },
            {
                "_id": 0,
                "user_message": 1,
                "assistant_message": 1,
                "created_at": 1,
            },
        )
        .sort("_id", -1)
        .limit(limit)
    )

    documents.reverse()

    for document in documents:
        document["created_at"] = (
            document["created_at"].isoformat()
        )

    return documents
