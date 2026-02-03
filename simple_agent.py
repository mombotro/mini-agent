"""Simplified Ollama Agent (no heavy dependencies)"""
import ollama
import sys
import time
import threading
import subprocess
from datetime import datetime
from typing import Optional, Dict, List
from simple_memory import SimpleMemory
from config import OLLAMA_MODEL, SOUL_PATH


class ThinkingIndicator:
    """Animated thinking indicator to show processing"""

    def __init__(self, message="Agent: Thinking"):
        self.message = message
        self.running = False
        self.thread = None

    def _animate(self):
        """Animate the thinking indicator"""
        dots = 0
        while self.running:
            # Clear line and print message with animated dots
            sys.stdout.write('\r' + ' ' * 80)  # Clear line
            sys.stdout.write('\r' + self.message + '.' * dots + ' ' * (3 - dots))
            sys.stdout.flush()
            dots = (dots + 1) % 4
            time.sleep(0.5)
        # Clear the thinking line when done
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()

    def start(self):
        """Start the thinking animation"""
        self.running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the thinking animation"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)


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
             include_context: bool = True) -> tuple[str, bool, bool]:
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

        # Get response from Ollama with thinking indicator
        thinking = ThinkingIndicator()
        thinking.start()

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            agent_response = response['message']['content']
        except Exception as e:
            agent_response = f"Error connecting to Ollama: {e}\n\nMake sure Ollama is running and the model '{self.model}' is available."
        finally:
            thinking.stop()

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": agent_response})

        # Save to memory
        soul_updated = False
        compacted = False
        if save_to_memory:
            self.memory.add_conversation(user_message, agent_response)
            soul_updated = self.memory.update_soul_if_needed()
            compacted = self.memory._check_auto_compact()

        return agent_response, soul_updated, compacted

    def learn_fact(self, fact: str, category: Optional[str] = None) -> tuple[str, bool, bool]:
        """Explicitly teach the agent a fact"""
        result = self.memory.add_fact(fact, category)
        soul_updated = self.memory.update_soul_if_needed()
        compacted = self.memory._check_auto_compact()
        return (f"Learned: {fact}" + (f" (Category: {category})" if category else ""), soul_updated, compacted)

    def complete_task(self, task: str, outcome: Optional[str] = None) -> tuple[str, bool, bool]:
        """Record a completed task"""
        result = self.memory.add_task(task, status="completed", outcome=outcome)
        soul_updated = self.memory.update_soul_if_needed()
        compacted = self.memory._check_auto_compact()
        return (f"Task recorded: {task}", soul_updated, compacted)

    def search_memories(self, query: str, limit: int = 5, include_archive: bool = False) -> List[Dict]:
        """Search through the agent's memories"""
        return self.memory.search_memory(query, limit=limit, include_archive=include_archive)

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


def auto_git_commit():
    """Automatically commit changes to git on quit"""
    try:
        # Check if there are changes to commit
        status = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True, check=True)

        if status.stdout.strip():
            # There are changes, commit them
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto-save agent session - {timestamp}\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)

            # Commit with message
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)

            print("\n[GIT] Changes automatically committed")
            return True
    except subprocess.CalledProcessError:
        # Git command failed, might not be a git repo or no git installed
        pass
    except Exception as e:
        # Silent fail - don't interrupt the quit process
        pass
    return False


def main():
    """Interactive agent interface"""
    print("[*] Initializing Ollama Agent with Memory Layer...\n")

    agent = SimpleAgent()

    # Show memory status on startup
    stats = agent.analyze_growth()
    total_memories = stats['total_memories']
    mem_stats = agent.memory.get_stats()

    print(f"[+] Agent initialized! (Model: {agent.model})")
    if total_memories > 0:
        if mem_stats['archive'] > 0:
            print(f"[MEMORY] Loaded {mem_stats['hot']} hot + {mem_stats['archive']} archived memories")
        else:
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
                auto_git_commit()
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
                print("\n  /search <query> [--archive]")
                print("    Search through stored memories")
                print("    Add --archive to search archive too")
                print("    Example: /search Python --archive")
                print("\n  /stats")
                print("    Show memory growth statistics")
                print("    Displays hot/archive counts and knowledge areas")
                print("\n  /compact")
                print("    Manually compact memories (move old to archive)")
                print("    Auto-compaction happens at 1000 memories")
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

            elif user_input.lower().startswith("/learn "):
                fact = user_input[7:]
                message, soul_updated, compacted = agent.learn_fact(fact)
                print(f"\n[LEARNED] {message}")
                if compacted:
                    stats = agent.memory.get_stats()
                    print(f"  Memory organized: {stats['hot']} active, {stats['archive']} archived")

            elif user_input.lower().startswith("/task "):
                task = user_input[6:]
                message, soul_updated, compacted = agent.complete_task(task)
                print(f"\n[TASK] {message}")
                if compacted:
                    stats = agent.memory.get_stats()
                    print(f"  Memory organized: {stats['hot']} active, {stats['archive']} archived")

            elif user_input.lower().startswith("/search "):
                query_parts = user_input[8:].strip()
                include_archive = "--archive" in query_parts
                query = query_parts.replace("--archive", "").strip()

                results = agent.search_memories(query, include_archive=include_archive)
                print(f"\n[SEARCH] Found {len(results)} memories:")
                for i, result in enumerate(results, 1):
                    source = " [ARCHIVE]" if result.get('_from_archive') else ""
                    print(f"\n{i}.{source} {result.get('text', '')}")

            elif user_input.lower() == "/stats":
                stats = agent.analyze_growth()
                mem_stats = agent.memory.get_stats()
                print("\n[STATS] Growth Statistics:")
                print(f"  Hot Storage: {mem_stats['hot']} memories")
                print(f"  Archive: {mem_stats['archive']} memories")
                print(f"  Total: {mem_stats['total']} memories")
                print(f"\n  Conversations: {stats['conversations']}")
                print(f"  Facts: {stats['facts']}")
                print(f"  Tasks: {stats['tasks']}")
                if stats['knowledge_areas']:
                    print(f"\n  I've been learning about:")
                    for area, count in stats['knowledge_areas'].items():
                        print(f"    • {area}: {count} {'fact' if count == 1 else 'facts'}")

            elif user_input.lower() == "/compact":
                stats_before = agent.memory.get_stats()
                compact_stats = agent.memory.compact_memories(force=True)
                print(f"\n[COMPACT] Compaction completed")
                print(f"  Moved: {compact_stats['moved']} memories to archive")
                print(f"  Hot storage: {compact_stats['hot']} memories")
                print(f"  Archive: {compact_stats['archive']} memories")

            else:
                response, soul_updated, compacted = agent.chat(user_input)
                print("\nAgent: " + response)
                if compacted:
                    stats = agent.memory.get_stats()
                    print(f"\n  (Memory organized: {stats['hot']} active, {stats['archive']} archived)")

        except KeyboardInterrupt:
            print("\n")
            auto_git_commit()
            print("Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
