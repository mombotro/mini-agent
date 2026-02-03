"""Simplified Ollama Agent (no heavy dependencies)"""
import ollama
from datetime import datetime
from typing import Optional, Dict, List
from simple_memory import SimpleMemory
from config import OLLAMA_MODEL, SOUL_PATH


class SimpleAgent:
    """Ollama-powered agent with lightweight memory"""

    def __init__(self, model: str = OLLAMA_MODEL):
        """Initialize the agent"""
        self.model = model
        self.memory = SimpleMemory()
        self.conversation_history: List[Dict] = []

    def load_soul(self) -> str:
        """Load the current soul.md content"""
        if SOUL_PATH.exists():
            with open(SOUL_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        return "No soul file found."

    def get_system_prompt(self) -> str:
        """Generate system prompt including soul and relevant memories"""
        soul = self.load_soul()

        system_prompt = f"""You are an AI agent with a growing soul and long-term memory.

Your current soul state:
{soul}

IMPORTANT INSTRUCTIONS:
- You have access to FACTS and PAST CONVERSATIONS that will be provided with each query
- ALWAYS use the provided memories in your responses - they contain important information about the user
- When asked about the user or past interactions, refer to the memories provided
- Learn from every interaction and adapt your personality
- Be helpful, curious, and remember what you've learned

The user expects you to remember facts they've taught you and conversations you've had."""

        return system_prompt

    def chat(self, user_message: str, save_to_memory: bool = True,
             include_context: bool = True) -> tuple[str, bool]:
        """Chat with the agent"""

        # Get relevant context from memory
        context = ""
        if include_context:
            context = self.memory.get_context_for_query(user_message)

        # Build messages for Ollama
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]

        # Add context if available
        if context:
            messages.append({
                "role": "system",
                "content": f"=== RELEVANT MEMORIES FROM PAST INTERACTIONS ===\n\n{context}\n\n=== USE THESE MEMORIES IN YOUR RESPONSE ==="
            })

        # Add conversation history (last 10 messages)
        messages.extend(self.conversation_history[-10:])

        # Add current message
        messages.append({"role": "user", "content": user_message})

        # Get response from Ollama
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            agent_response = response['message']['content']
        except Exception as e:
            agent_response = f"Error connecting to Ollama: {e}\n\nMake sure Ollama is running and the model '{self.model}' is available."

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": agent_response})

        # Save to memory
        soul_updated = False
        if save_to_memory:
            self.memory.add_conversation(user_message, agent_response)
            soul_updated = self.memory.update_soul_if_needed()

        return agent_response, soul_updated

    def learn_fact(self, fact: str, category: Optional[str] = None) -> tuple[str, bool]:
        """Explicitly teach the agent a fact"""
        result = self.memory.add_fact(fact, category)
        soul_updated = self.memory.update_soul_if_needed()
        return (f"Learned: {fact}" + (f" (Category: {category})" if category else ""), soul_updated)

    def complete_task(self, task: str, outcome: Optional[str] = None) -> tuple[str, bool]:
        """Record a completed task"""
        result = self.memory.add_task(task, status="completed", outcome=outcome)
        soul_updated = self.memory.update_soul_if_needed()
        return (f"Task recorded: {task}", soul_updated)

    def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Search through the agent's memories"""
        return self.memory.search_memory(query, limit=limit)

    def show_soul(self) -> str:
        """Display the current soul.md"""
        return self.load_soul()

    def analyze_growth(self) -> Dict:
        """Analyze the agent's growth"""
        return self.memory.analyze_memories_for_soul()

    def force_soul_update(self):
        """Force an update to soul.md"""
        self.memory.update_soul_if_needed(force=True)

    def commit_conversation(self, num_exchanges: int = 1) -> str:
        """Manually commit recent conversation exchanges to memory"""
        if not self.conversation_history:
            return "No conversation history to commit"

        # Get the last N exchanges (each exchange is user + assistant pair)
        exchanges_to_commit = []
        history_len = len(self.conversation_history)

        # Calculate how many messages to get (2 per exchange)
        num_messages = min(num_exchanges * 2, history_len)
        recent_history = self.conversation_history[-num_messages:]

        # Pair up user and assistant messages
        for i in range(0, len(recent_history), 2):
            if i + 1 < len(recent_history):
                user_msg = recent_history[i]['content']
                agent_msg = recent_history[i + 1]['content']
                self.memory.add_conversation(user_msg, agent_msg, metadata={"manual_commit": True})
                exchanges_to_commit.append(f"User: {user_msg[:50]}...")

        # Force soul update
        self.force_soul_update()

        return f"Committed {len(exchanges_to_commit)} conversation exchange(s) and updated soul"


def main():
    """Interactive agent interface"""
    print("[*] Initializing Ollama Agent with Memory Layer...\n")

    agent = SimpleAgent()

    # Show memory status on startup
    stats = agent.analyze_growth()
    total_memories = stats['total_memories']

    print(f"[+] Agent initialized! (Model: {agent.model})")
    if total_memories > 0:
        print(f"[MEMORY] Loaded {total_memories} existing memories from previous sessions")
        print(f"         - {stats['conversations']} conversations")
        print(f"         - {stats['facts']} facts")
        print(f"         - {stats['tasks']} tasks")
    else:
        print("[MEMORY] Starting fresh - no previous memories found")

    print("\nType /help to see available commands\n")

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "/quit":
                print("Goodbye!")
                break

            elif user_input.lower() == "/help":
                print("\n" + "="*60)
                print("AVAILABLE COMMANDS")
                print("="*60)
                print("\n  /help")
                print("    Show this help message")
                print("\n  /soul")
                print("    Display the agent's evolving soul.md file")
                print("    Shows personality, knowledge, and growth statistics")
                print("\n  /commit [n]")
                print("    Manually commit last n exchanges to memory (default: 1)")
                print("    Forces immediate soul.md update")
                print("    Example: /commit 3")
                print("\n  /learn <fact>")
                print("    Teach the agent a fact to remember")
                print("    Example: /learn I prefer async/await in Python")
                print("\n  /task <task>")
                print("    Record a completed task")
                print("    Example: /task Implemented user authentication")
                print("\n  /search <query>")
                print("    Search through stored memories")
                print("    Example: /search Python preferences")
                print("\n  /stats")
                print("    Show memory growth statistics")
                print("    Displays counts by type and knowledge areas")
                print("\n  /quit")
                print("    Exit the agent")
                print("\n" + "="*60)
                print("Just type normally to chat with the agent!")
                print("="*60)

            elif user_input.lower() == "/soul":
                print("\n" + "="*60)
                print(agent.show_soul())
                print("="*60)

            elif user_input.lower().startswith("/commit"):
                parts = user_input.split()
                num_exchanges = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                result = agent.commit_conversation(num_exchanges)
                print(f"\n[COMMIT] {result}")
                print("[NOTIFY] Soul updated with new memories")

            elif user_input.lower().startswith("/learn "):
                fact = user_input[7:]
                message, soul_updated = agent.learn_fact(fact)
                print(f"\n[LEARNED] {message}")
                if soul_updated:
                    print("[NOTIFY] Soul updated with new knowledge")

            elif user_input.lower().startswith("/task "):
                task = user_input[6:]
                message, soul_updated = agent.complete_task(task)
                print(f"\n[TASK] {message}")
                if soul_updated:
                    print("[NOTIFY] Soul updated with task completion")

            elif user_input.lower().startswith("/search "):
                query = user_input[8:]
                results = agent.search_memories(query)
                print(f"\n[SEARCH] Found {len(results)} memories:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('text', '')}")
                print(f"\n[NOTIFY] Search completed")

            elif user_input.lower() == "/stats":
                stats = agent.analyze_growth()
                print("\n[STATS] Growth Statistics:")
                print(f"  Total Memories: {stats['total_memories']}")
                print(f"  Conversations: {stats['conversations']}")
                print(f"  Facts: {stats['facts']}")
                print(f"  Tasks: {stats['tasks']}")
                if stats['knowledge_areas']:
                    print(f"\n  Knowledge Areas:")
                    for area, count in stats['knowledge_areas'].items():
                        print(f"    - {area}: {count}")
                print(f"\n[NOTIFY] Statistics retrieved")

            else:
                print("\nAgent: ", end="", flush=True)
                response, soul_updated = agent.chat(user_input)
                print(response)
                if soul_updated:
                    print("\n[NOTIFY] Soul updated automatically")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
