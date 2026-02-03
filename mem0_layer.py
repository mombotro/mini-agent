"""Memory Layer for Ollama Agent using Mem0"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from mem0 import Memory
from config import MEMORY_CONFIG, SOUL_PATH, SOUL_UPDATE_FREQUENCY


class Mem0Layer:
    """Memory management layer for the agent"""

    def __init__(self):
        """Initialize the memory layer"""
        self.memory = Memory.from_config(MEMORY_CONFIG)
        self.interaction_count = 0
        self.user_id = "default_user"

    def add_conversation(self, user_message: str, agent_response: str, metadata: Optional[Dict] = None) -> str:
        """Store a conversation exchange"""
        conversation = f"User: {user_message}\nAgent: {agent_response}"
        result = self.memory.add(
            conversation,
            user_id=self.user_id,
            metadata={
                "type": "conversation",
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
        )
        self.interaction_count += 1
        return result

    def add_fact(self, fact: str, category: Optional[str] = None) -> str:
        """Store a learned fact"""
        result = self.memory.add(
            fact,
            user_id=self.user_id,
            metadata={
                "type": "fact",
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
        )
        return result

    def add_task(self, task: str, status: str = "completed", outcome: Optional[str] = None) -> str:
        """Store a task and its outcome"""
        task_data = f"Task: {task}\nStatus: {status}"
        if outcome:
            task_data += f"\nOutcome: {outcome}"

        result = self.memory.add(
            task_data,
            user_id=self.user_id,
            metadata={
                "type": "task",
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        )
        return result

    def search_memory(self, query: str, limit: int = 5, memory_type: Optional[str] = None) -> List[Dict]:
        """Search through memories"""
        filters = {"user_id": self.user_id}
        if memory_type:
            filters["type"] = memory_type

        results = self.memory.search(query, user_id=self.user_id, limit=limit)
        return results

    def get_all_memories(self) -> List[Dict]:
        """Retrieve all memories"""
        return self.memory.get_all(user_id=self.user_id)

    def get_context_for_query(self, query: str, max_results: int = 5) -> str:
        """Get relevant context from memory for a query"""
        results = self.search_memory(query, limit=max_results)

        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            memory_text = result.get('memory', result.get('text', ''))
            context_parts.append(f"[Memory {i}]: {memory_text}")

        return "\n".join(context_parts)

    def analyze_memories_for_soul(self) -> Dict[str, Any]:
        """Analyze memories to extract insights for soul.md"""
        all_memories = self.get_all_memories()

        analysis = {
            "total_memories": len(all_memories),
            "conversations": 0,
            "facts": 0,
            "tasks": 0,
            "personality_insights": [],
            "knowledge_areas": {},
            "interaction_patterns": []
        }

        for memory in all_memories:
            metadata = memory.get('metadata', {})
            mem_type = metadata.get('type', 'unknown')

            if mem_type == "conversation":
                analysis["conversations"] += 1
            elif mem_type == "fact":
                analysis["facts"] += 1
                category = metadata.get('category', 'general')
                analysis["knowledge_areas"][category] = analysis["knowledge_areas"].get(category, 0) + 1
            elif mem_type == "task":
                analysis["tasks"] += 1

        return analysis

    def update_soul_if_needed(self, force: bool = False):
        """Update soul.md if enough interactions have occurred"""
        if force or self.interaction_count % SOUL_UPDATE_FREQUENCY == 0:
            self._update_soul()

    def _update_soul(self):
        """Update the soul.md file with current insights"""
        analysis = self.analyze_memories_for_soul()

        # Read current soul
        if SOUL_PATH.exists():
            with open(SOUL_PATH, 'r', encoding='utf-8') as f:
                soul_content = f.read()
        else:
            soul_content = self._get_initial_soul_template()

        # Update statistics
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Simple updates - replace statistics section
        stats_section = f"""## Memory Statistics

- **Total Memories**: {analysis['total_memories']}
- **Conversations Tracked**: {analysis['conversations']}
- **Facts Learned**: {analysis['facts']}
- **Tasks Completed**: {analysis['tasks']}"""

        # Update total interactions
        soul_content = soul_content.replace(
            f"**Total Interactions**: {self.interaction_count - 1}",
            f"**Total Interactions**: {self.interaction_count}"
        )
        soul_content = soul_content.replace(
            "**Total Interactions**: 0",
            f"**Total Interactions**: {self.interaction_count}"
        )

        # Update last updated
        if "**Last Updated**:" in soul_content:
            import re
            soul_content = re.sub(
                r'\*\*Last Updated\*\*: .*',
                f'**Last Updated**: {timestamp}',
                soul_content
            )

        # Update statistics section
        if "## Memory Statistics" in soul_content:
            import re
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
                soul_content = soul_content.replace(
                    "*Knowledge grows through conversations*",
                    knowledge_list if knowledge_list else "*Knowledge grows through conversations*"
                )

        # Add evolution log entry
        if analysis['total_memories'] > 0 and analysis['total_memories'] % 10 == 0:
            milestone = f"- **{timestamp}**: Reached {analysis['total_memories']} total memories ({analysis['conversations']} conversations, {analysis['facts']} facts, {analysis['tasks']} tasks)"
            if "## Evolution Log" in soul_content and milestone not in soul_content:
                soul_content = soul_content.replace(
                    "## Evolution Log\n\n*Notable milestones in the agent's development*\n\n",
                    f"## Evolution Log\n\n*Notable milestones in the agent's development*\n\n{milestone}\n"
                )

        # Write updated soul
        with open(SOUL_PATH, 'w', encoding='utf-8') as f:
            f.write(soul_content)

    def _get_initial_soul_template(self) -> str:
        """Get initial soul.md template"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        template = Path(__file__).parent / "soul.md"
        if template.exists():
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                return content.replace("{{ timestamp }}", timestamp)
        return f"# Agent Soul\n\nCreated: {timestamp}\n"
