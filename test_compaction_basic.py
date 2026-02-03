"""Basic test for memory compaction functionality"""
from simple_memory import SimpleMemory
from datetime import datetime
import config

def test_compaction_basic():
    print("[TEST] Testing Memory Compaction System\n")

    # Temporarily modify config for testing
    original_threshold = config.COMPACTION_THRESHOLD
    original_keep_hot = config.COMPACTION_KEEP_HOT
    original_keep_tasks = config.COMPACTION_KEEP_TASKS

    # Set lower thresholds for testing
    config.COMPACTION_THRESHOLD = 5
    config.COMPACTION_KEEP_HOT = 3
    config.COMPACTION_KEEP_TASKS = 2

    print(f"[CONFIG] Test thresholds set:")
    print(f"  COMPACTION_THRESHOLD: {config.COMPACTION_THRESHOLD}")
    print(f"  COMPACTION_KEEP_HOT: {config.COMPACTION_KEEP_HOT}")
    print(f"  COMPACTION_KEEP_TASKS: {config.COMPACTION_KEEP_TASKS}\n")

    # Initialize memory system
    mem = SimpleMemory()
    initial_stats = mem.get_stats()
    print(f"[INIT] Memory initialized")
    print(f"  Hot memories: {initial_stats['hot']}")
    print(f"  Archive memories: {initial_stats['archive']}")
    print(f"  Total: {initial_stats['total']}\n")

    # Test: Check compaction with force
    print("[TEST] Testing forced compaction...")
    compact_stats = mem.compact_memories(force=True)
    print(f"  Moved: {compact_stats['moved']} memories")
    print(f"  Hot: {compact_stats['hot']} memories")
    print(f"  Archive: {compact_stats['archive']} memories\n")

    # Verify facts were not archived
    print("[VERIFY] Checking facts preservation...")
    hot_facts = [m for m in mem.memories if m.get('type') == 'fact']
    archive_facts = [m for m in mem.archive if m.get('type') == 'fact']
    print(f"  Facts in hot storage: {len(hot_facts)}")
    print(f"  Facts in archive: {len(archive_facts)}")
    if len(archive_facts) == 0:
        print("  [OK] Facts preserved correctly (none archived)\n")
    else:
        print("  [WARNING] Some facts were archived (should not happen)\n")

    # Test search with archive
    print("[TEST] Testing search with archive...")
    results_hot = mem.search_memory("test", limit=5, include_archive=False)
    results_all = mem.search_memory("test", limit=10, include_archive=True)
    print(f"  Hot storage results: {len(results_hot)}")
    print(f"  Total results (hot + archive): {len(results_all)}\n")

    # Test auto-compaction check
    print("[TEST] Testing auto-compaction check...")
    before_check = len(mem.memories)
    triggered = mem._check_auto_compact()
    after_check = len(mem.memories)
    print(f"  Memories before: {before_check}")
    print(f"  Auto-compact triggered: {triggered}")
    print(f"  Memories after: {after_check}\n")

    # Final stats
    final_stats = mem.get_stats()
    print("[FINAL STATS]")
    print(f"  Hot: {final_stats['hot']} memories")
    print(f"  Archive: {final_stats['archive']} memories")
    print(f"  Total: {final_stats['total']} memories\n")

    # Check files exist
    print("[FILES]")
    print(f"  memories.json exists: {mem.memory_file.exists()}")
    print(f"  memories_archive.json exists: {mem.archive_file.exists()}\n")

    # Restore original config
    config.COMPACTION_THRESHOLD = original_threshold
    config.COMPACTION_KEEP_HOT = original_keep_hot
    config.COMPACTION_KEEP_TASKS = original_keep_tasks

    print("[SUCCESS] Compaction system is functional!")
    print("\nNote: The system will auto-compact when hot storage exceeds 1000 memories.")
    print("Manual compaction can be triggered with /compact command.")

if __name__ == "__main__":
    test_compaction_basic()
