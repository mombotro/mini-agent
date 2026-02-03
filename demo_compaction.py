"""Demo script showing memory compaction features"""
from simple_agent import SimpleAgent
import config

def demo_compaction():
    print("\n" + "="*70)
    print("MEMORY COMPACTION SYSTEM DEMO")
    print("="*70 + "\n")

    # Initialize agent
    print("[1] Initializing agent...")
    agent = SimpleAgent()

    # Show current status
    mem_stats = agent.memory.get_stats()
    print(f"\n[STATUS] Current Memory State")
    print(f"  Hot storage: {mem_stats['hot']} memories")
    print(f"  Archive: {mem_stats['archive']} memories")
    print(f"  Total: {mem_stats['total']} memories")

    # Show configuration
    print(f"\n[CONFIG] Compaction Settings")
    print(f"  Auto-compact enabled: {config.AUTO_COMPACT_ENABLED}")
    print(f"  Threshold: {config.COMPACTION_THRESHOLD} memories")
    print(f"  Keep hot: {config.COMPACTION_KEEP_HOT} conversations")
    print(f"  Keep tasks: {config.COMPACTION_KEEP_TASKS} tasks")

    # Demonstrate search without archive
    print(f"\n[2] Searching hot storage only...")
    results = agent.search_memories("test", limit=3, include_archive=False)
    print(f"  Found {len(results)} results in hot storage")

    # Demonstrate search with archive
    print(f"\n[3] Searching hot + archive...")
    results_all = agent.search_memories("test", limit=5, include_archive=True)
    archive_count = sum(1 for r in results_all if r.get('_from_archive'))
    print(f"  Found {len(results_all)} total results")
    print(f"  From hot: {len(results_all) - archive_count}")
    print(f"  From archive: {archive_count}")

    # Show detailed stats
    print(f"\n[4] Detailed Statistics")
    stats = agent.analyze_growth()
    print(f"  Conversations: {stats['conversations']}")
    print(f"  Facts: {stats['facts']} (never archived)")
    print(f"  Tasks: {stats['tasks']}")

    # Demonstrate manual compaction
    print(f"\n[5] Manual Compaction Demo")
    before = agent.memory.get_stats()
    print(f"  Before: Hot={before['hot']}, Archive={before['archive']}")

    compact_result = agent.memory.compact_memories(force=True)
    after = agent.memory.get_stats()
    print(f"  After: Hot={after['hot']}, Archive={after['archive']}")
    print(f"  Moved: {compact_result['moved']} memories")

    # Verify facts preservation
    print(f"\n[6] Verifying Facts Preservation")
    hot_facts = [m for m in agent.memory.memories if m.get('type') == 'fact']
    archive_facts = [m for m in agent.memory.archive if m.get('type') == 'fact']
    print(f"  Facts in hot: {len(hot_facts)}")
    print(f"  Facts in archive: {len(archive_facts)}")
    if len(archive_facts) == 0:
        print(f"  [OK] All facts preserved in hot storage")

    # Show files
    print(f"\n[7] Storage Files")
    print(f"  Hot: {agent.memory.memory_file}")
    print(f"    Exists: {agent.memory.memory_file.exists()}")
    print(f"  Archive: {agent.memory.archive_file}")
    print(f"    Exists: {agent.memory.archive_file.exists()}")

    # Performance comparison
    print(f"\n[8] Performance Benefits")
    print(f"  Hot storage size: {mem_stats['hot']} memories")
    print(f"  Search complexity: O({mem_stats['hot']}) vs O({mem_stats['total']}) before")
    if mem_stats['total'] > 0:
        speedup = mem_stats['total'] / max(mem_stats['hot'], 1)
        print(f"  Estimated speedup: {speedup:.1f}x faster")

    # Usage examples
    print(f"\n[9] Available Commands")
    print(f"  /stats              - View hot/archive statistics")
    print(f"  /search <query>     - Search hot storage only")
    print(f"  /search <query> --archive - Search hot + archive")
    print(f"  /compact            - Manual compaction")

    # Summary
    print(f"\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"The compaction system keeps your agent fast by maintaining a small")
    print(f"hot storage ({config.COMPACTION_KEEP_HOT} conversations) while preserving all")
    print(f"memories in searchable archive. Facts are never archived, ensuring")
    print(f"important context is always available.")
    print(f"\nAuto-compaction triggers at {config.COMPACTION_THRESHOLD} memories.")
    print(f"Current status: {mem_stats['hot']} hot, {mem_stats['archive']} archived")
    print("="*70 + "\n")

if __name__ == "__main__":
    demo_compaction()
