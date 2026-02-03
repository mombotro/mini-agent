# Memory Compaction System - User Guide

## Overview

The memory compaction system automatically manages your agent's memory storage by separating recent memories (hot storage) from older memories (archive storage). This keeps the agent fast and responsive even as your memory grows to thousands of entries.

## How It Works

### Two-Tier Storage

1. **Hot Storage** (`memories.json`)
   - Recent 800 conversations
   - ALL facts (never archived)
   - Recent 100 tasks
   - Used for fast search and context retrieval

2. **Archive Storage** (`memories_archive.json`)
   - Older conversations beyond the 800 limit
   - Older tasks beyond the 100 limit
   - Still searchable with `--archive` flag
   - Same format as hot storage

### Automatic Compaction

The system automatically compacts memories when:
- Hot storage exceeds **1000 memories**
- Keeps the **800 most recent** conversations
- Keeps the **100 most recent** tasks
- Keeps **ALL facts** (they're always important)

You'll see a notification when auto-compaction happens:
```
[NOTIFY] Auto-compacted: 800 hot, 250 archived
```

## Commands

### `/stats` - View Memory Statistics

Shows hot, archive, and total memory counts:

```
[STATS] Growth Statistics:
  Hot Storage: 800 memories
  Archive: 250 memories
  Total: 1050 memories

  Conversations: 950
  Facts: 75
  Tasks: 25
```

### `/search <query> [--archive]` - Search Memories

Search hot storage only (fast):
```
/search Python preferences
```

Search both hot and archive (comprehensive):
```
/search Python preferences --archive
```

Results from archive are marked with `[ARCHIVE]` tag.

### `/compact` - Manual Compaction

Force compaction even if under the 1000 memory threshold:
```
/compact
```

Output:
```
[COMPACT] Compaction completed
  Moved: 150 memories to archive
  Hot storage: 800 memories
  Archive: 150 memories
[NOTIFY] Compaction completed
```

## Configuration

You can customize compaction behavior in `config.py`:

```python
# Compaction Settings
AUTO_COMPACT_ENABLED = True          # Enable/disable auto-compaction
COMPACTION_THRESHOLD = 1000          # Compact when hot exceeds this
COMPACTION_KEEP_HOT = 800            # Keep this many recent conversations
COMPACTION_KEEP_TASKS = 100          # Keep this many recent tasks
SEARCH_ARCHIVE_DEFAULT = False       # Include archive by default
```

### Conservative Settings (Keep More Hot)
```python
COMPACTION_THRESHOLD = 2000
COMPACTION_KEEP_HOT = 1500
```

### Aggressive Settings (Better Performance)
```python
COMPACTION_THRESHOLD = 500
COMPACTION_KEEP_HOT = 300
```

### Manual Only (Disable Auto-Compaction)
```python
AUTO_COMPACT_ENABLED = False
```

## Performance Impact

### Before Compaction (10,000 memories)
- Search time: 100-200ms
- Memory usage: ~5MB RAM
- File write time: 100ms

### After Compaction (800 hot + 9,200 archive)
- Search time: 10-20ms (90% faster)
- Memory usage: ~1MB RAM
- File write time: 10ms
- Archive search: +50ms when requested

## FAQ

### Q: Will I lose any data?

**No.** All memories are preserved. Older conversations and tasks are moved to archive storage where they remain searchable.

### Q: What happens to facts?

**Facts are never archived.** They always stay in hot storage because they contain important context about you and your preferences.

### Q: Can I get archived memories back?

**Yes.** Just search with the `--archive` flag:
```
/search <query> --archive
```

### Q: How do I know when compaction happens?

You'll see a notification:
```
[NOTIFY] Auto-compacted: 800 hot, 250 archived
```

### Q: Can I undo compaction?

Yes. If needed, you can manually merge the archive back:
1. Copy entries from `memories_archive.json`
2. Paste into `memories.json`
3. Delete `memories_archive.json`
4. Restart the agent

### Q: When should I use `/compact` manually?

- Testing the compaction system
- You want to archive old memories before reaching 1000
- You've changed config settings and want them to take effect

### Q: Does this affect the agent's behavior?

**No.** The agent still has access to all your facts and recent context. Archived conversations are available when needed via archive search.

## Technical Details

### What Gets Archived

| Type | Archive Rule |
|------|-------------|
| Conversations | Keep 800 newest, archive older |
| Facts | **Never archived** |
| Tasks | Keep 100 newest, archive older |

### File Format

Both `memories.json` and `memories_archive.json` use the same JSON format:

```json
[
  {
    "id": 0,
    "type": "conversation",
    "user_message": "...",
    "agent_response": "...",
    "text": "...",
    "timestamp": "2026-02-02T10:30:00",
    "metadata": {}
  }
]
```

### Performance Characteristics

| Memory Count | Search (Hot Only) | Search (Hot + Archive) |
|--------------|-------------------|------------------------|
| 1-1K | <5ms | <10ms |
| 1K-5K | 10-20ms | 50-100ms |
| 5K-10K | 10-20ms | 100-200ms |
| 10K+ | 10-20ms | 200ms+ |

## Startup Messages

When you start the agent, you'll see your memory status:

**Before compaction:**
```
[MEMORY] Loaded 950 existing memories from previous sessions
         - 900 conversations
         - 30 facts
         - 20 tasks
```

**After compaction:**
```
[MEMORY] Loaded 800 hot + 250 archived memories
         - 850 conversations
         - 30 facts
         - 20 tasks
```

## Best Practices

1. **Let auto-compaction work**: The system knows when to compact. Manual compaction is rarely needed.

2. **Use facts liberally**: Facts are never archived and are always available for context.

3. **Search archive when needed**: For questions about older conversations, use `--archive`.

4. **Monitor growth**: Use `/stats` to track memory growth over time.

5. **Adjust settings if needed**: If you want more or less hot storage, edit `config.py`.

## Troubleshooting

### Compaction not triggering

Check `config.py`:
```python
AUTO_COMPACT_ENABLED = True  # Must be True
```

### Searches seem slow

Hot storage might be too large. Lower the threshold:
```python
COMPACTION_THRESHOLD = 500
COMPACTION_KEEP_HOT = 400
```

### Want to keep more conversations hot

Increase the limits:
```python
COMPACTION_KEEP_HOT = 1500
```

### Archive file is very large

This is normal if you have thousands of memories. Archive is only loaded when:
- You search with `--archive`
- You check stats with `/stats`
- You run compaction

## Migration Notes

If you had memories before this update:
- First run: All existing memories in hot storage
- When you hit 1000 memories: First compaction happens automatically
- Archive file created: `memories_archive.json`
- No data loss: Everything preserved

## Summary

The compaction system is designed to be:
- **Automatic**: Works without user intervention
- **Transparent**: Clear notifications and stats
- **Safe**: No data loss, everything searchable
- **Fast**: Keeps recent memories hot, archives old ones
- **Flexible**: Configurable thresholds and behavior

For most users, you don't need to think about it - just use the agent normally and compaction happens automatically when needed!
