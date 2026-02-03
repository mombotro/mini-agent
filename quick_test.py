"""Quick test to verify memory recall"""
from simple_agent import SimpleAgent

print("Testing memory recall...\n")
agent = SimpleAgent()

print("\n" + "="*60)
print("Testing context retrieval for 'family':")
print("="*60)
context = agent.memory.get_context_for_query("family")
print(context)

print("\n" + "="*60)
print("Testing context retrieval for 'children':")
print("="*60)
context = agent.memory.get_context_for_query("children")
print(context)

print("\n" + "="*60)
print("All facts stored:")
print("="*60)
facts = [m for m in agent.memory.memories if m.get('type') == 'fact']
for fact in facts:
    print(f"- {fact.get('text')}")
