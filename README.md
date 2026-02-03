# Ollama Agent with Memory & Growing Soul

A persistent memory agent powered by Ollama that remembers conversations, learns facts, and evolves its personality over time through a growing `soul.md` file.

## Features

- **Long-term Memory**: Remembers all conversations, facts, and tasks across sessions
- **Growing Soul**: `soul.md` file that evolves with personality traits, knowledge areas, and relationship patterns
- **Context-Aware**: Automatically retrieves relevant memories for each conversation
- **Lightweight**: JSON-based storage, no heavy dependencies
- **Persistent**: Survives restarts - all memories and knowledge are preserved
- **Interactive Commands**: Rich command set for memory management

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running ([ollama.com](https://ollama.com))
3. **Git** (for cloning/pushing to GitHub)

### Installation

1. **Clone the repository**:
```bash
git clone <your-private-repo-url>
cd agent
```

2. **Install dependencies**:
```bash
pip install ollama
```

3. **Pull an Ollama model** (if you don't have one):
```bash
# Recommended: Fast lightweight model
ollama pull llama3.2:1b

# Or other options:
ollama pull mistral
ollama pull phi3:mini
```

4. **Run the agent**:
```bash
python simple_agent.py
```

Or on Windows, double-click:
```
start_agent.bat
```

## Usage

### First Time Setup

When you first run the agent, it will show:
```
[*] Initializing Ollama Agent with Memory Layer...

[+] Agent initialized! (Model: llama3.2:1b)
[MEMORY] Starting fresh - no previous memories found

Type /help to see available commands
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show all available commands | `/help` |
| `/soul` | Display the agent's evolving soul.md | `/soul` |
| `/commit [n]` | Manually commit last n exchanges to memory | `/commit 3` |
| `/learn <fact>` | Teach the agent a fact | `/learn I prefer Python over JavaScript` |
| `/task <task>` | Record a completed task | `/task Built authentication system` |
| `/search <query>` | Search through memories | `/search Python preferences` |
| `/stats` | Show memory growth statistics | `/stats` |
| `/quit` | Exit the agent | `/quit` |

### Example Session

```
You: Hi! My name is Alex and I'm a Python developer.
Agent: Hello Alex! Nice to meet you...

You: /learn I prefer FastAPI for building APIs

[LEARNED] Learned: I prefer FastAPI for building APIs
[NOTIFY] Soul updated with new knowledge

You: /task Completed user authentication module

[TASK] Task recorded: Completed user authentication module

You: What do you know about my tech preferences?
Agent: Based on our conversations, I know you're Alex, a Python developer
       who prefers using FastAPI for building APIs...

You: /stats

[STATS] Growth Statistics:
  Total Memories: 3
  Conversations: 1
  Facts: 1
  Tasks: 1

  Knowledge Areas:
    - general: 1

You: /soul
============================================================
# Agent Soul

**Created**: 2026-02-02 17:09:45
**Total Interactions**: 3
**Last Updated**: 2026-02-02 18:45:10

## Memory Statistics
- **Total Memories**: 3
- **Conversations Tracked**: 1
- **Facts Learned**: 1
- **Tasks Completed**: 1
============================================================
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    simple_agent.py                      │
│              (Main agent interface)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌─────────────────┐    ┌──────────────────┐
│ simple_memory.py│    │   Ollama API     │
│ (Memory layer)  │    │  (LLM inference) │
└────────┬────────┘    └──────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│soul.md  │ │memories  │
│         │ │.json     │
└─────────┘ └──────────┘
```

### Memory System

1. **Conversations**: Every exchange is stored with timestamps
2. **Facts**: Explicitly taught information with optional categories
3. **Tasks**: Completed work with outcomes
4. **Auto-Context**: Relevant memories automatically retrieved for each query
5. **Soul Updates**: Every 5 interactions (configurable), `soul.md` updates with insights

### File Structure

```
agent/
├── simple_agent.py          # Main agent interface
├── simple_memory.py         # Memory management layer
├── config.py                # Configuration settings
├── soul.md                  # The agent's evolving soul
├── memory_store/
│   └── memories.json        # All stored memories
├── requirements-simple.txt  # Python dependencies
├── start_agent.bat          # Windows launcher
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Configuration

Edit `config.py` to customize:

```python
# Change the Ollama model
OLLAMA_MODEL = "llama3.2:1b"  # or "mistral", "phi3:mini", etc.

# Change soul update frequency
SOUL_UPDATE_FREQUENCY = 5  # Updates every N interactions

# Memory storage location
MEMORY_DIR = BASE_DIR / "memory_store"
```

## Memory Persistence

All data persists across sessions:

- **Memories**: `memory_store/memories.json` (all conversations, facts, tasks)
- **Soul**: `soul.md` (personality, knowledge, statistics)
- **On Restart**: Agent loads all previous memories and shows summary

Example restart:
```
[+] Agent initialized! (Model: llama3.2:1b)
[MEMORY] Loaded 25 existing memories from previous sessions
         - 18 conversations
         - 5 facts
         - 2 tasks
```

## Advanced Usage

### Teaching Facts with Categories

Organize knowledge by category:
```
You: /learn Team uses Docker for deployment
```

Categories help the agent organize knowledge areas in `soul.md`.

### Manual Memory Commits

Force immediate soul updates:
```
You: /commit
[COMMIT] Committed 1 conversation exchange(s) and updated soul
[NOTIFY] Soul updated with new memories
```

Commit multiple exchanges:
```
You: /commit 5
```

### Searching Memories

Find past conversations or facts:
```
You: /search Docker
[SEARCH] Found 3 memories:

1. [FACT]: Team uses Docker for deployment
2. [PAST CONVERSATION]
   User: How do we deploy applications?
   Agent: Based on what I know...
```

## Notifications

The agent provides real-time feedback:

- `[NOTIFY] Soul updated automatically` - After 5 interactions
- `[NOTIFY] Soul updated with new knowledge` - When learning triggers update
- `[NOTIFY] Soul updated with task completion` - When tasks trigger update
- `[NOTIFY] Soul updated with new memories` - Manual commits
- `[NOTIFY] Search completed` - After memory searches
- `[NOTIFY] Statistics retrieved` - After viewing stats

## Troubleshooting

### "Error connecting to Ollama"

**Problem**: Ollama is not running or model not available

**Solution**:
1. Check Ollama is running: `ollama list`
2. Pull the model: `ollama pull llama3.2:1b`
3. Verify model name in `config.py` matches available model

### "No memories found" after restart

**Problem**: Memories not persisting

**Solution**:
1. Check `memory_store/memories.json` exists
2. Verify file permissions
3. Run `python test_memory.py` to diagnose

### Agent not remembering taught facts

**Problem**: Context not being retrieved

**Solution**:
1. Use `/search <fact>` to verify fact was saved
2. Check `soul.md` shows facts learned
3. Facts are automatically included in context for all queries

### Slow responses

**Problem**: Model taking too long

**Solution**:
1. Switch to smaller model: `ollama pull llama3.2:1b`
2. Update `config.py` with faster model
3. Check system resources

## Development

### Testing Memory System

```bash
# Test memory persistence
python test_memory.py

# Test search functionality
python test_search.py

# Test context retrieval
python quick_test.py
```

### Extending the Agent

Add custom commands in `simple_agent.py`:

```python
elif user_input.lower().startswith("/mycmd"):
    # Your custom command logic
    print("[MYCMD] Command executed")
```

Add custom memory types in `simple_memory.py`:

```python
def add_custom_type(self, data: str) -> str:
    memory = {
        "id": len(self.memories),
        "type": "custom",
        "text": data,
        "timestamp": datetime.now().isoformat()
    }
    self.memories.append(memory)
    self._save_memories()
    return str(memory["id"])
```

## Requirements

- **Python**: 3.8 or higher
- **Ollama**: Latest version
- **Disk Space**: ~100MB for model + memories
- **RAM**: 2GB minimum (4GB recommended for larger models)

## License

MIT License - See LICENSE file for details

## Contributing

This is a private repository. For questions or issues, contact the repository owner.

## Changelog

### v1.0.0 (2026-02-02)
- Initial release
- JSON-based memory storage
- Growing soul.md system
- Interactive command interface
- Memory persistence across sessions
- Context-aware conversations
- Real-time notifications

## Tips

1. **Teach facts explicitly** using `/learn` for important information
2. **Check `/stats` regularly** to see agent growth
3. **Review `soul.md`** to see personality evolution
4. **Use `/commit`** after important conversations to force soul updates
5. **Search memories** with `/search` to verify what the agent remembers
6. **Categories help** - use them when learning facts for better organization

## Support

For issues, bugs, or feature requests, please open an issue in the GitHub repository.

---

**Built with Ollama** - Local LLM inference
**Inspired by mem0** - Memory for AI agents
