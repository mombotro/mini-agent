"""Simple JSON-based memory layer (no heavy dependencies)"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import SOUL_PATH, SOUL_UPDATE_FREQUENCY, MEMORY_DIR


class SimpleMemory:
    """Lightweight memory management using JSON"""

    def __init__(self):
        """Initialize the memory layer"""
        self.memory_file = MEMORY_DIR / "memories.json"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memories = self._load_memories()
        # Initialize interaction count from existing conversation memories
        self.interaction_count = sum(1 for m in self.memories if m.get('type') == 'conversation')
        self.user_id = "default_user"

    def _load_memories(self) -> List[Dict]:
        """Load memories from JSON file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_memories(self):
        """Save memories to JSON file"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, indent=2, ensure_ascii=False)

    def add_conversation(self, user_message: str, agent_response: str, metadata: Optional[Dict] = None) -> str:
        """Store a conversation exchange"""
        memory = {
            "id": len(self.memories),
            "type": "conversation",
            "user_message": user_message,
            "agent_response": agent_response,
            "text": f"User: {user_message}\nAgent: {agent_response}",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.memories.append(memory)
        self._save_memories()
        self.interaction_count += 1
        return str(memory["id"])

    def add_fact(self, fact: str, category: Optional[str] = None) -> str:
        """Store a learned fact"""
        memory = {
            "id": len(self.memories),
            "type": "fact",
            "text": fact,
            "category": category or "general",
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }
        self.memories.append(memory)
        self._save_memories()
        return str(memory["id"])

    def add_task(self, task: str, status: str = "completed", outcome: Optional[str] = None) -> str:
        """Store a task and its outcome"""
        memory = {
            "id": len(self.memories),
            "type": "task",
            "text": task,
            "status": status,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }
        self.memories.append(memory)
        self._save_memories()
        return str(memory["id"])

    def search_memory(self, query: str, limit: int = 5, memory_type: Optional[str] = None) -> List[Dict]:
        """Simple keyword search through memories"""
        query_lower = query.lower()
        query_words = query_lower.split()
        results = []

        for memory in self.memories:
            if memory_type and memory.get("type") != memory_type:
                continue

            # Search in text and also in user_message/agent_response for conversations
            text = memory.get("text", "").lower()
            user_msg = memory.get("user_message", "").lower()
            agent_msg = memory.get("agent_response", "").lower()

            combined_text = f"{text} {user_msg} {agent_msg}"

            # Check if any query word matches
            matches = sum(1 for word in query_words if word in combined_text)

            if matches > 0:
                memory_copy = memory.copy()
                memory_copy["_score"] = matches
                results.append(memory_copy)

        # Sort by relevance
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return results[:limit]

    def get_all_memories(self) -> List[Dict]:
        """Retrieve all memories"""
        return self.memories

    def get_context_for_query(self, query: str, max_results: int = 8) -> str:
        """Get relevant context from memory for a query"""
        # Get both query-specific memories and recent important facts
        query_results = self.search_memory(query, limit=max_results)

        # Also get all facts (they're usually important for context)
        fact_memories = [m for m in self.memories if m.get('type') == 'fact']

        # Combine and deduplicate
        seen_ids = set()
        combined_results = []

        # Add query results first (they're most relevant)
        for result in query_results:
            mem_id = result.get('id')
            if mem_id not in seen_ids:
                seen_ids.add(mem_id)
                combined_results.append(result)

        # Add facts that weren't already included
        for fact in fact_memories[-5:]:  # Last 5 facts
            mem_id = fact.get('id')
            if mem_id not in seen_ids:
                seen_ids.add(mem_id)
                combined_results.append(fact)

        if not combined_results:
            return ""

        context_parts = []
        for i, result in enumerate(combined_results[:max_results], 1):
            mem_type = result.get('type', 'unknown')
            if mem_type == 'fact':
                text = f"[FACT]: {result.get('text', '')}"
            elif mem_type == 'conversation':
                user_msg = result.get('user_message', '')
                agent_msg = result.get('agent_response', '')
                text = f"[PAST CONVERSATION]\nUser: {user_msg}\nAgent: {agent_msg[:200]}..."
            else:
                text = f"[{mem_type.upper()}]: {result.get('text', '')}"

            context_parts.append(text)

        return "\n\n".join(context_parts)

    def analyze_memories_for_soul(self) -> Dict[str, Any]:
        """Analyze memories to extract insights for soul.md"""
        analysis = {
            "total_memories": len(self.memories),
            "conversations": 0,
            "facts": 0,
            "tasks": 0,
            "personality_insights": [],
            "knowledge_areas": {},
            "interaction_patterns": []
        }

        for memory in self.memories:
            mem_type = memory.get('type', 'unknown')

            if mem_type == "conversation":
                analysis["conversations"] += 1
            elif mem_type == "fact":
                analysis["facts"] += 1
                category = memory.get('category', 'general')
                analysis["knowledge_areas"][category] = analysis["knowledge_areas"].get(category, 0) + 1
            elif mem_type == "task":
                analysis["tasks"] += 1

        return analysis

    def update_soul_if_needed(self, force: bool = False) -> bool:
        """Update soul.md if enough interactions have occurred"""
        if force or self.interaction_count % SOUL_UPDATE_FREQUENCY == 0:
            self._update_soul()
            return True
        return False

    def _update_soul(self):
        """Update the soul.md file with current insights"""
        analysis = self.analyze_memories_for_soul()

        # Read current soul
        if SOUL_PATH.exists():
            with open(SOUL_PATH, 'r', encoding='utf-8') as f:
                soul_content = f.read()
        else:
            return

        # Update statistics
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Simple updates - replace statistics section
        stats_section = f"""## Memory Statistics

- **Total Memories**: {analysis['total_memories']}
- **Conversations Tracked**: {analysis['conversations']}
- **Facts Learned**: {analysis['facts']}
- **Tasks Completed**: {analysis['tasks']}"""

        # Update total interactions
        import re
        soul_content = re.sub(
            r'\*\*Total Interactions\*\*: \d+',
            f"**Total Interactions**: {self.interaction_count}",
            soul_content
        )

        # Update last updated
        if "**Last Updated**:" in soul_content:
            soul_content = re.sub(
                r'\*\*Last Updated\*\*: .*',
                f'**Last Updated**: {timestamp}',
                soul_content
            )

        # Update statistics section
        if "## Memory Statistics" in soul_content:
            soul_content = re.sub(
                r'## Memory Statistics.*?(?=\n---|\n## |$)',
                stats_section + '\n\n',
                soul_content,
                flags=re.DOTALL
            )

        # Add knowledge areas if we have any
        if analysis['knowledge_areas']:
            knowledge_list = "\n".join([f"- **{area}**: {count} facts"
                                       for area, count in sorted(analysis['knowledge_areas'].items())])

            if "### Learned Knowledge" in soul_content:
                soul_content = re.sub(
                    r'### Learned Knowledge\n\*Knowledge grows through conversations\*',
                    f'### Learned Knowledge\n\n{knowledge_list}',
                    soul_content
                )

        # Add evolution log entry
        if analysis['total_memories'] > 0 and analysis['total_memories'] % 10 == 0:
            milestone = f"- **{timestamp}**: Reached {analysis['total_memories']} total memories ({analysis['conversations']} conversations, {analysis['facts']} facts, {analysis['tasks']} tasks)"
            if "## Evolution Log" in soul_content and milestone not in soul_content:
                soul_content = soul_content.replace(
                    "- **2026-02-02 17:09:45**: Agent initialized, ready to learn and grow",
                    f"- **2026-02-02 17:09:45**: Agent initialized, ready to learn and grow\n{milestone}"
                )

        # Write updated soul
        with open(SOUL_PATH, 'w', encoding='utf-8') as f:
            f.write(soul_content)
