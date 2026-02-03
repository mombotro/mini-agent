"""Configuration for the Ollama Agent with Mem0"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
SOUL_PATH = BASE_DIR / "soul.md"
MEMORY_DIR = BASE_DIR / "memory_store"

# Ollama Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "moondream")  # Vision-capable model
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Memory Configuration
MEMORY_CONFIG = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "agent_memory",
            "path": str(MEMORY_DIR),
        }
    }
}

# Soul Evolution Settings
SOUL_UPDATE_FREQUENCY = 5  # Update soul.md every N interactions
PERSONALITY_TRAITS_MAX = 10
KNOWLEDGE_AREAS_MAX = 20

# Compaction Settings
AUTO_COMPACT_ENABLED = True
COMPACTION_THRESHOLD = 1000  # Compact when hot storage exceeds this
COMPACTION_KEEP_HOT = 800     # Keep this many recent conversations in hot storage
COMPACTION_KEEP_TASKS = 100   # Keep this many recent tasks in hot storage
SEARCH_ARCHIVE_DEFAULT = False  # Include archive in searches by default
