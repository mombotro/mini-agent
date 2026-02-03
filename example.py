"""Example usage of the Ollama Agent with Mem0"""
from agent import OllamaAgent


def demo():
    """Demonstrate the agent's capabilities"""
    print("🚀 Ollama Agent with Mem0 - Demo\n")

    # Initialize agent
    agent = OllamaAgent()

    # Example 1: Regular conversation
    print("=" * 60)
    print("Example 1: Basic Conversation")
    print("=" * 60)
    response = agent.chat("Hi! My name is Alex and I love Python programming.")
    print(f"Agent: {response}\n")

    # Example 2: Teaching facts
    print("=" * 60)
    print("Example 2: Teaching Facts")
    print("=" * 60)
    agent.learn_fact("Alex prefers async/await over callbacks", category="preferences")
    agent.learn_fact("Alex is building a web scraper project", category="projects")
    print("✓ Facts learned\n")

    # Example 3: Recording tasks
    print("=" * 60)
    print("Example 3: Recording Tasks")
    print("=" * 60)
    agent.complete_task(
        "Set up Python virtual environment",
        outcome="Successfully created venv with Python 3.11"
    )
    agent.complete_task(
        "Install required packages",
        outcome="Installed requests, beautifulsoup4, and selenium"
    )
    print("✓ Tasks recorded\n")

    # Example 4: Contextual conversation using memory
    print("=" * 60)
    print("Example 4: Memory-Enhanced Conversation")
    print("=" * 60)
    response = agent.chat("What do you know about my coding style?")
    print(f"Agent: {response}\n")

    # Example 5: Search memories
    print("=" * 60)
    print("Example 5: Searching Memories")
    print("=" * 60)
    results = agent.search_memories("Python")
    print(f"Found {len(results)} memories about Python:")
    for i, result in enumerate(results[:3], 1):
        memory = result.get('memory', result.get('text', ''))
        print(f"  {i}. {memory[:100]}...")
    print()

    # Example 6: View growth statistics
    print("=" * 60)
    print("Example 6: Growth Statistics")
    print("=" * 60)
    stats = agent.analyze_growth()
    print(f"Total Memories: {stats['total_memories']}")
    print(f"Conversations: {stats['conversations']}")
    print(f"Facts: {stats['facts']}")
    print(f"Tasks: {stats['tasks']}")
    if stats['knowledge_areas']:
        print("\nKnowledge Areas:")
        for area, count in stats['knowledge_areas'].items():
            print(f"  - {area}: {count} facts")
    print()

    # Example 7: Force soul update
    print("=" * 60)
    print("Example 7: Updating Soul")
    print("=" * 60)
    agent.force_soul_update()
    print("✓ Soul updated - check soul.md to see the evolution\n")

    # Example 8: Show soul snippet
    print("=" * 60)
    print("Example 8: Soul Preview")
    print("=" * 60)
    soul = agent.show_soul()
    # Show first few lines
    lines = soul.split('\n')[:15]
    print('\n'.join(lines))
    print("...\n(See soul.md for complete content)\n")


if __name__ == "__main__":
    demo()
