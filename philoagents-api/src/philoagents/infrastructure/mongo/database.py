from functools import lru_cache

from loguru import logger
from pymongo import MongoClient

from philoagents.config import settings


@lru_cache(maxsize=1)
def get_database():
    """One pooled, reconnecting client shared by every synchronous Mongo reader."""
    client = MongoClient(settings.MONGO_URI, appname="philoagents")
    logger.info(f"Opened MongoDB client for database {settings.MONGO_DB_NAME}")
    return client[settings.MONGO_DB_NAME]
