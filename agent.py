"""Ollama Agent with Mem0 Integration"""
import ollama
from datetime import datetime
from typing import Optional, Dict, List
from mem0_layer import Mem0Layer
from config import OLLAMA_MODEL, SOUL_PATH


class OllamaAgent:
    """Ollama-powered agent with long-term memory"""

    def __init__(self, model: str = OLLAMA_MODEL):
        """Initialize the agent"""
        self.model = model
        self.memory = Mem0Layer()
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

Remember:
- Learn from every interaction
- Store important facts and insights
- Track tasks you complete
- Develop your personality through experiences
- Build understanding of user preferences

Be helpful, curious, and let your personality grow naturally through interactions."""

        return system_prompt

    def chat(self, user_message: str, save_to_memory: bool = True,
             include_context: bool = True) -> str:
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
                "content": f"Relevant memories:\n{context}"
            })

        # Add conversation history (last 5 exchanges)
        messages.extend(self.conversation_history[-10:])

        # Add current message
        messages.append({"role": "user", "content": user_message})

        # Get response from Ollama
        response = ollama.chat(
            model=self.model,
            messages=messages
        )

        agent_response = response['message']['content']

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": agent_response})

        # Save to memory
        if save_to_memory:
            self.memory.add_conversation(user_message, agent_response)
            self.memory.update_soul_if_needed()

        return agent_response

    def learn_fact(self, fact: str, category: Optional[str] = None) -> str:
        """Explicitly teach the agent a fact"""
        result = self.memory.add_fact(fact, category)
        self.memory.update_soul_if_needed()
        return f"Learned: {fact}" + (f" (Category: {category})" if category else "")

    def complete_task(self, task: str, outcome: Optional[str] = None) -> str:
        """Record a completed task"""
        result = self.memory.add_task(task, status="completed", outcome=outcome)
        self.memory.update_soul_if_needed()
        return f"Task recorded: {task}"

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


def main():
    """Example usage"""
    print("🤖 Initializing Ollama Agent with Mem0...\n")

    agent = OllamaAgent()

    print("Agent initialized! Try chatting with it.")
    print("Commands:")
    print("  /soul - Show the agent's soul")
    print("  /learn <fact> - Teach the agent a fact")
    print("  /task <task> - Record a completed task")
    print("  /search <query> - Search memories")
    print("  /stats - Show growth statistics")
    print("  /quit - Exit\n")

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "/quit":
                print("👋 Goodbye!")
                break

            elif user_input.lower() == "/soul":
                print("\n" + "="*50)
                print(agent.show_soul())
                print("="*50)

            elif user_input.lower().startswith("/learn "):
                fact = user_input[7:]
                print(f"\n🧠 {agent.learn_fact(fact)}")

            elif user_input.lower().startswith("/task "):
                task = user_input[6:]
                print(f"\n✅ {agent.complete_task(task)}")

            elif user_input.lower().startswith("/search "):
                query = user_input[8:]
                results = agent.search_memories(query)
                print(f"\n🔍 Found {len(results)} memories:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('memory', result.get('text', ''))}")

            elif user_input.lower() == "/stats":
                stats = agent.analyze_growth()
                print("\n📊 Growth Statistics:")
                print(f"  Total Memories: {stats['total_memories']}")
                print(f"  Conversations: {stats['conversations']}")
                print(f"  Facts: {stats['facts']}")
                print(f"  Tasks: {stats['tasks']}")
                if stats['knowledge_areas']:
                    print(f"\n  Knowledge Areas:")
                    for area, count in stats['knowledge_areas'].items():
                        print(f"    - {area}: {count}")

            else:
                print("\n🤖 Agent: ", end="", flush=True)
                response = agent.chat(user_input)
                print(response)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
