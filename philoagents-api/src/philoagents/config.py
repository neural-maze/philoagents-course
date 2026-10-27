from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )

    # --- Qwen (DashScope OpenAI-compatible) Configuration ---
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen3.8-flash"

    # --- Legacy provider configuration, only used by the evaluation scripts ---
    GROQ_API_KEY: str = ""
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_LLM_MODEL_CONTEXT_SUMMARY: str = "llama-3.1-8b-instant"
    OPENAI_API_KEY: str = ""

    # --- MongoDB Configuration ---
    MONGO_URI: str = Field(
        default="mongodb://philoagents:philoagents@local_dev_atlas:27017/?directConnection=true",
        description="Connection URI for the local MongoDB Atlas instance.",
    )
    MONGO_DB_NAME: str = "philoagents"
    MONGO_STATE_CHECKPOINT_COLLECTION: str = "philosopher_state_checkpoints"
    MONGO_STATE_WRITES_COLLECTION: str = "philosopher_state_writes"
    MONGO_LONG_TERM_MEMORY_COLLECTION: str = "philosopher_long_term_memory"
    MONGO_CHAT_HISTORY_COLLECTION: str = "chat_history"

    # --- HTTP surface configuration ---
    # Comma separated, and it must list the origin the UI is actually served from: compose
    # publishes it on 8088, `npm run dev` on 8080. "*" is only valid without credentials.
    CORS_ORIGINS: str = (
        "http://localhost:8080,http://localhost:8088,http://127.0.0.1:8088"
    )
    MAX_MESSAGE_CHARS: int = 2000
    RATE_LIMIT_MAX_MESSAGES: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    # Session minting is keyed on client IP, so it needs headroom for a shared network.
    RATE_LIMIT_MAX_SESSIONS: int = 60

    # --- Session authentication ---
    # Empty means the API accepts unauthenticated calls, which is only acceptable on a
    # laptop: a client-supplied player_id is trivially rotated, so the rate limit keyed on
    # it stops nobody. Set this before publishing the game anywhere reachable.
    SESSION_SECRET: str = ""
    SESSION_TTL_SECONDS: int = 12 * 3600

    # --- Comet ML & Opik Configuration ---
    COMET_API_KEY: str | None = Field(
        default=None, description="API key for Comet ML and Opik services."
    )
    COMET_PROJECT: str = Field(
        default="philoagents_course",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- Agents Configuration ---
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 30
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5

    # --- RAG Configuration ---
    RAG_TEXT_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_TEXT_EMBEDDING_MODEL_DIM: int = 384
    RAG_TOP_K: int = 3
    RAG_DEVICE: str = "cpu"
    RAG_CHUNK_SIZE: int = 256

    # --- Paths Configuration ---
    EVALUATION_DATASET_FILE_PATH: Path = Path("data/evaluation_dataset.json")
    EXTRACTION_METADATA_FILE_PATH: Path = Path("data/extraction_metadata.json")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def auth_enabled(self) -> bool:
        return bool(self.SESSION_SECRET)


settings = Settings()
