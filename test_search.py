"""Test search functionality"""
from simple_memory import SimpleMemory

memory = SimpleMemory()

# Test searches
queries = [
    "family",
    "children",
    "Nexa",
    "name",
    "what did I teach you"
]

print("Testing memory search...\n")
print(f"Total memories: {len(memory.memories)}\n")

for query in queries:
    print(f"Query: '{query}'")
    print("=" * 60)
    results = memory.search_memory(query, limit=3)
    print(f"Found {len(results)} results\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. Type: {result.get('type')}")
        print(f"   Score: {result.get('_score')}")
        text = result.get('text', '')[:150]
        print(f"   Text: {text}...")
        print()

    print()
