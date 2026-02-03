# Quick Start Guide

Your Ollama agent with mem0 layer and growing soul.md is ready!

## Starting the Agent

### Option 1: Double-click the batch file
```
start_agent.bat
```

### Option 2: Run from command line
```bash
python simple_agent.py
```

## What You Can Do

### 1. Chat Naturally
Just type your messages and the agent will respond with context from previous conversations.

```
You: Hi, I'm working on a machine learning project
Agent: [responds]

You: What frameworks should I use?
Agent: [responds with memory of your ML project]
```

### 2. Manually Commit to Memory
Use `/commit` to manually save recent conversation(s) to memory and force a soul update:

```
You: What's the best way to handle async operations?
Agent: [provides detailed response]

You: /commit
[COMMIT] Committed 1 conversation exchange(s) and updated soul
```

Commit multiple exchanges:
```
You: /commit 3
[COMMIT] Committed 3 conversation exchange(s) and updated soul
```

This is useful when:
- You want to ensure important conversations are saved
- You want to immediately update soul.md with new insights
- The conversation isn't being auto-saved (save_to_memory=False)

### 3. Teach Facts
Use `/learn` to explicitly teach the agent information:

```
You: /learn I prefer TensorFlow over PyTorch
[LEARNED] Learned: I prefer TensorFlow over PyTorch

You: /learn Project deadline is March 15th
[LEARNED] Learned: Project deadline is March 15th (Category: None)
```

You can add categories:
```
You: /learn Team uses Docker for deployment
[LEARNED] Learned: Team uses Docker for deployment (Category: deployment)
```

### 4. Track Tasks
Record completed tasks and their outcomes:

```
You: /task Set up Python virtual environment
[TASK] Task recorded: Set up Python virtual environment

You: /task Implemented user authentication with JWT tokens
[TASK] Task recorded: Implemented user authentication with JWT tokens
```

### 5. Search Memories
Find relevant past conversations and facts:

```
You: /search Python
[SEARCH] Found 3 memories:

1. User: Hi, I'm working on a machine learning project
   Agent: [response]

2. I prefer TensorFlow over PyTorch

3. User: What frameworks should I use?
   Agent: [response]
```

### 6. View Growth Stats
See how your agent's memory is growing:

```
You: /stats
[STATS] Growth Statistics:
  Total Memories: 15
  Conversations: 10
  Facts: 3
  Tasks: 2

  Knowledge Areas:
    - deployment: 2
    - preferences: 4
```

### 7. Check Your Agent's Soul
View the evolving soul.md:

```
You: /soul
==================================================
# Agent Soul

**Created**: 2026-02-02 17:09:45
**Total Interactions**: 15
**Last Updated**: 2026-02-02 17:35:22

## Personality Traits
[Shows emerging personality]

## Knowledge Base
[Shows learned knowledge by category]

## Memory Statistics
- **Total Memories**: 15
- **Conversations Tracked**: 10
- **Facts Learned**: 3
- **Tasks Completed**: 2

## Evolution Log
- **2026-02-02 17:09:45**: Agent initialized
- **2026-02-02 17:25:10**: Reached 10 total memories
==================================================
```

## How Memory Works

1. **Automatic Context**: When you chat, the agent searches memories for relevant context
2. **Soul Updates**: Every 5 interactions, soul.md automatically updates with insights
3. **Persistent Storage**: All memories stored in `memory_store/memories.json`
4. **Growing Knowledge**: Categories and patterns emerge naturally from your interactions

## Tips

- Be specific when teaching facts - the agent will remember exactly what you tell it
- Use categories with `/learn` to organize knowledge areas
- Check `/stats` periodically to see your agent's growth
- Review `soul.md` to see how personality and knowledge evolve
- The more you interact, the better the context becomes

## Files Created

- `memory_store/memories.json` - All memories (conversations, facts, tasks)
- `soul.md` - The agent's growing soul and personality
- `simple_agent.py` - Main agent program
- `simple_memory.py` - Memory layer implementation
- `config.py` - Configuration (model, update frequency)

## Customization

Edit `config.py` to customize:
- `OLLAMA_MODEL` - Change the model (current: ministral-3:8b)
- `SOUL_UPDATE_FREQUENCY` - How often soul.md updates (current: every 5 interactions)

## Example Full Session

```
[*] Initializing Ollama Agent with Memory Layer...

[+] Agent initialized! Try chatting with it.

Commands:
  /soul - Show the agent's soul
  /learn <fact> - Teach the agent a fact
  /task <task> - Record a completed task
  /search <query> - Search memories
  /stats - Show growth statistics
  /quit - Exit

You: Hello! I'm Alex, a Python developer working on web applications.

Agent: Hello Alex! It's great to meet you. As a Python developer...

You: /learn I prefer FastAPI for building APIs

[LEARNED] Learned: I prefer FastAPI for building APIs

You: /task Completed user authentication system with JWT

[TASK] Task recorded: Completed user authentication system with JWT

You: What do you know about my work?

Agent: Based on our conversations, I know you're Alex, a Python developer...

You: /stats

[STATS] Growth Statistics:
  Total Memories: 4
  Conversations: 2
  Facts: 1
  Tasks: 1

You: /quit
Goodbye!
```

Start chatting and watch your agent's soul grow!
