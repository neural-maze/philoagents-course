from philoagents.infrastructure.opik_utils import configure

configure()

try:
    import importlib_metadata

    __version__ = importlib_metadata.version("philoagents")
except Exception:
    __version__ = "0.0.0"
