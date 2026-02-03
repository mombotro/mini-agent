"""Test script to verify memory persistence"""
from simple_memory import SimpleMemory
from config import MEMORY_DIR
import json

print("Testing memory persistence...\n")

# Initialize memory
memory = SimpleMemory()

print(f"Memory file location: {memory.memory_file}")
print(f"Loaded {len(memory.memories)} memories\n")

if memory.memories:
    print("Existing memories:")
    print("=" * 60)
    for i, mem in enumerate(memory.memories, 1):
        mem_type = mem.get('type', 'unknown')
        timestamp = mem.get('timestamp', 'no timestamp')
        print(f"\n{i}. Type: {mem_type}")
        print(f"   Time: {timestamp}")

        if mem_type == 'conversation':
            user_msg = mem.get('user_message', '')
            agent_msg = mem.get('agent_response', '')
            print(f"   User: {user_msg[:100]}...")
            print(f"   Agent: {agent_msg[:100]}...")
        elif mem_type == 'fact':
            print(f"   Fact: {mem.get('text', '')}")
            print(f"   Category: {mem.get('category', 'none')}")
        elif mem_type == 'task':
            print(f"   Task: {mem.get('text', '')}")
            print(f"   Status: {mem.get('status', 'unknown')}")

    print("\n" + "=" * 60)
    print(f"\nTotal: {len(memory.memories)} memories")
else:
    print("No memories found. The agent will start fresh.")
    print("Memories will be saved to:")
    print(f"  {memory.memory_file}")
