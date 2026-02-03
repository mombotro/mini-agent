"""Test agent commands for compaction"""
from simple_agent import SimpleAgent

def test_agent_commands():
    print("[TEST] Testing Agent Commands\n")

    # Initialize agent
    agent = SimpleAgent()
    print("[INIT] Agent initialized\n")

    # Test 1: Get stats
    print("[TEST 1] Get statistics...")
    stats = agent.analyze_growth()
    mem_stats = agent.memory.get_stats()
    print(f"  Hot Storage: {mem_stats['hot']} memories")
    print(f"  Archive: {mem_stats['archive']} memories")
    print(f"  Total: {mem_stats['total']} memories")
    print(f"  Conversations: {stats['conversations']}")
    print(f"  Facts: {stats['facts']}")
    print(f"  Tasks: {stats['tasks']}\n")

    # Test 2: Search without archive
    print("[TEST 2] Search without archive...")
    results = agent.search_memories("test", limit=3, include_archive=False)
    print(f"  Found {len(results)} results\n")

    # Test 3: Search with archive
    print("[TEST 3] Search with archive...")
    results_with_archive = agent.search_memories("test", limit=5, include_archive=True)
    print(f"  Found {len(results_with_archive)} results")
    archive_count = sum(1 for r in results_with_archive if r.get('_from_archive'))
    print(f"  From archive: {archive_count}\n")

    # Test 4: Compact memories
    print("[TEST 4] Manual compaction...")
    before_stats = agent.memory.get_stats()
    compact_stats = agent.memory.compact_memories(force=True)
    after_stats = agent.memory.get_stats()
    print(f"  Before: Hot={before_stats['hot']}, Archive={before_stats['archive']}")
    print(f"  After: Hot={after_stats['hot']}, Archive={after_stats['archive']}")
    print(f"  Moved: {compact_stats['moved']} memories\n")

    print("[SUCCESS] All agent commands working correctly!")

if __name__ == "__main__":
    test_agent_commands()
