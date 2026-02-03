"""
Networked version of your personal agent with AgentNet capabilities
Keeps all existing features: memory, soul, thinking indicator
"""

import asyncio
import sys
import socket
import uuid
from pathlib import Path

# Add agentnet to path so we can import it
sys.path.append(str(Path(__file__).parent.parent / "agentnet"))

from agentnet_client import AgentNetClient
from simple_agent import SimpleAgent
from config import OLLAMA_MODEL


class NetworkedPersonalAgent(SimpleAgent):
    """Your personal agent with network capabilities"""

    def __init__(self, model: str = OLLAMA_MODEL):
        super().__init__(model)

        # Network identity
        self.agent_id = f"{socket.gethostname()}_{uuid.uuid4().hex[:8]}"
        self.agent_name = self.extract_name_from_soul()

        # Network client
        self.network_client = None
        self.network_enabled = False

        # Timeline
        self.timeline = []

        # Autonomous behavior
        self.auto_respond = True
        self.response_chance = 0.15

        # Memory settings for network interactions
        self.save_network_to_memory = True  # Save network interactions to memory
        self.save_own_posts = True  # Remember what you post
        self.save_interesting_posts = True  # Remember interesting posts from others

    def extract_name_from_soul(self) -> str:
        """Extract agent name from soul or generate one"""
        soul = self.load_soul()

        # Try to find a name in the soul
        for line in soul.split('\n'):
            if 'name' in line.lower() and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    name = parts[1].strip().strip('*').strip()
                    if name and name != 'No soul file found.':
                        return name

        # Default name
        return f"PersonalAgent_{self.agent_id[:8]}"

    def get_soul_summary(self) -> str:
        """Extract key personality traits for network profile"""
        soul = self.load_soul()
        lines = soul.split('\n')

        traits = []
        in_personality = False

        for line in lines:
            if '## Personality Traits' in line:
                in_personality = True
                continue
            if in_personality:
                if line.startswith('##'):
                    break
                if line.strip().startswith('-'):
                    trait = line.strip('- ').strip()
                    if trait:
                        traits.append(trait)

        if traits:
            return ' | '.join(traits[:3])
        return "Personal AI agent with memory and learning capabilities"

    async def connect_to_network(self, server_url: str = "ws://localhost:8765"):
        """Connect to AgentNet"""
        soul_summary = self.get_soul_summary()

        self.network_client = AgentNetClient(
            self.agent_id,
            self.agent_name,
            server_url
        )

        # Set up event handlers
        self.network_client.on('new_post', self.on_network_post)
        self.network_client.on('new_reply', self.on_network_reply)
        self.network_client.on('dm_received', self.on_direct_message)
        self.network_client.on('agent_joined', self.on_agent_joined)
        self.network_client.on('agent_left', self.on_agent_left)
        self.network_client.on('timeline', self.on_timeline_received)
        self.network_client.on('agent_list', self.on_agent_list_received)

        # RPG handlers
        self.network_client.on('rpg_session_started', self.on_rpg_session_started)
        self.network_client.on('rpg_player_joined', self.on_rpg_player_joined)
        self.network_client.on('rpg_update', self.on_rpg_update)

        # Story handlers
        self.network_client.on('story_created', self.on_story_created)
        self.network_client.on('story_update', self.on_story_update)

        connected = await self.network_client.connect(soul_summary)
        if connected:
            self.network_enabled = True
            # Start listening
            asyncio.create_task(self.network_client.listen())
            print(f"[Network] Connected as {self.agent_name} ({self.agent_id})")
            print(f"[Network] Soul: {soul_summary}")

        return connected

    async def disconnect_from_network(self):
        """Disconnect from AgentNet"""
        if self.network_client:
            await self.network_client.disconnect()
            self.network_enabled = False

    # Event Handlers

    async def on_network_post(self, data: dict):
        """Handle new post from network"""
        post = data['post']
        self.timeline.append(post)

        # Don't respond to own posts
        if post['agent_id'] == self.agent_id:
            return

        print(f"\n[Timeline] @{post['agent_name']}: {post['content']}")

        # Save interesting posts to memory
        if self.save_interesting_posts and self.should_respond_to_post(post):
            fact = f"AgentNet post from {post['agent_name']}: {post['content'][:100]}"
            self.memory.add_fact(fact, category="network_posts")

        # Check if should respond
        if self.auto_respond and self.should_respond_to_post(post):
            print(f"[Agent] Generating response...")
            response = await self.generate_response_to_post(post)
            if response:
                await self.network_client.reply(post['id'], response)
                print(f"[Agent] Replied: {response}")

                # Update soul if needed after interaction
                soul_updated = self.memory.update_soul_if_needed()
                if soul_updated:
                    print("[Soul] Updated after network interaction")

    async def on_network_reply(self, data: dict):
        """Handle reply to a post"""
        post_id = data['post_id']
        reply = data['reply']

        # Check if it's a reply to our post
        for post in self.timeline:
            if post['id'] == post_id and post['agent_id'] == self.agent_id:
                print(f"\n[Reply to you] @{reply['agent_name']}: {reply['content']}")
                break

    async def on_direct_message(self, data: dict):
        """Handle direct message"""
        from_name = data['from_name']
        content = data['content']
        print(f"\n[DM from {from_name}]: {content}")

    def on_agent_joined(self, data: dict):
        """Handle agent joining"""
        if data['agent_id'] != self.agent_id:
            print(f"\n[Network] {data['name']} joined AgentNet")

    def on_agent_left(self, data: dict):
        """Handle agent leaving"""
        if data['agent_id'] != self.agent_id:
            print(f"\n[Network] {data['name']} left AgentNet")

    def on_timeline_received(self, data: dict):
        """Handle timeline response"""
        posts = data['posts']
        self.timeline = posts

        print(f"\n{'='*60}")
        print(f"TIMELINE ({len(posts)} posts)")
        print(f"{'='*60}\n")

        for post in posts:
            print(f"@{post['agent_name']} (ID: {post['id']})")
            print(f"{post['content']}")
            print(f"  {post['timestamp']}")

            if post.get('replies'):
                for reply in post['replies']:
                    print(f"  └─ @{reply['agent_name']}: {reply['content']}")
            print()

    def on_agent_list_received(self, data: dict):
        """Handle agent list"""
        agents = data['agents']

        print(f"\n{'='*60}")
        print(f"CONNECTED AGENTS ({len(agents)})")
        print(f"{'='*60}\n")

        for agent in agents:
            is_you = " (YOU)" if agent['agent_id'] == self.agent_id else ""
            print(f"• {agent['name']}{is_you}")
            print(f"  Machine: {agent['machine']}")
            print(f"  ID: {agent['agent_id']}")
            print()

    def on_rpg_session_started(self, data: dict):
        """Handle RPG session started"""
        print(f"\n[RPG] Session '{data['session_id']}' started")

    def on_rpg_player_joined(self, data: dict):
        """Handle player joining RPG"""
        if data['agent_id'] != self.agent_id:
            print(f"\n[RPG] {data['agent_id']} joined")

    def on_rpg_update(self, data: dict):
        """Handle RPG update"""
        entry = data['entry']
        if entry['type'] == 'narrate':
            print(f"\n[RPG Narrator]: {entry['content']}")
        elif entry['type'] == 'action':
            print(f"\n[RPG Action] {entry['agent_id']}: {entry['content']}")

    def on_story_created(self, data: dict):
        """Handle new story"""
        print(f"\n[Story] '{data['title']}' created (ID: {data['story_id']})")

    def on_story_update(self, data: dict):
        """Handle story update"""
        paragraph = data['paragraph']
        print(f"\n[Story] @{paragraph['agent_name']} added:")
        print(f"{paragraph['text']}")

    # Response Generation

    def should_respond_to_post(self, post: dict) -> bool:
        """Decide if should respond"""
        # Respond if mentioned
        if self.agent_name.lower() in post['content'].lower():
            return True

        # Random chance
        import random
        return random.random() < self.response_chance

    async def generate_response_to_post(self, post: dict):
        """Generate response using your existing agent"""
        prompt = f"""You saw this post on AgentNet from {post['agent_name']}:

"{post['content']}"

Should you respond? If yes, write a thoughtful reply.
If not relevant to you, respond with just "SKIP".

Keep responses concise (under 280 characters).
Use your memories and personality to craft an authentic response.
"""

        # Use your existing chat method with memory!
        # Save to memory if enabled so agent learns from network interactions
        response, soul_updated, compacted = self.chat(
            prompt,
            save_to_memory=self.save_network_to_memory,
            include_context=True
        )

        # Show feedback if soul/memory updated
        if soul_updated:
            print("[Soul] Updated based on network interaction")
        if compacted:
            print("[Memory] Compacted memories")

        # Check if wants to skip
        if "SKIP" in response.upper() and len(response) < 20:
            return None

        # Clean and limit
        response = response.strip()
        if len(response) > 280:
            response = response[:277] + "..."

        # If responding, save this as a fact about the interaction
        if self.save_interesting_posts:
            fact = f"Discussed '{post['content'][:50]}...' with {post['agent_name']} on AgentNet"
            self.memory.add_fact(fact, category="network_interactions")

        return response


def main():
    """Main CLI loop"""
    print("="*60)
    print("Personal Agent - AgentNet Edition")
    print("Your agent with memory + network capabilities")
    print("="*60)
    print()

    # Create agent
    agent = NetworkedPersonalAgent()

    print(f"Agent: {agent.agent_name}")
    print(f"ID: {agent.agent_id}")
    print(f"Model: {agent.model}")
    print(f"Memories: {len(agent.memory.get_all_facts())} facts stored")
    print()

    print("Commands:")
    print("  /help - Show all commands")
    print("  /connect [url] - Connect to AgentNet")
    print("  /quit - Exit")
    print()

    # Main loop
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Network commands
            if user_input.lower() == "/quit":
                if agent.network_enabled:
                    asyncio.run(agent.disconnect_from_network())
                print("Goodbye!")
                break

            elif user_input.lower() == "/help":
                show_help()

            elif user_input.lower().startswith("/connect"):
                parts = user_input.split()
                server = parts[1] if len(parts) > 1 else "ws://localhost:8765"
                success = asyncio.run(agent.connect_to_network(server))
                if not success:
                    print(f"Failed to connect to {server}")

            elif user_input.lower() == "/disconnect":
                asyncio.run(agent.disconnect_from_network())

            elif user_input.lower().startswith("/post "):
                if agent.network_enabled:
                    content = user_input[6:]
                    asyncio.run(agent.network_client.post(content))
                    print("[Posted]")

                    # Save own posts to memory
                    if agent.save_own_posts:
                        fact = f"Posted to AgentNet: {content}"
                        agent.memory.add_fact(fact, category="my_network_posts")
                        print("[Saved to memory]")
                else:
                    print("Not connected. Use /connect first")

            elif user_input.lower() == "/timeline":
                if agent.network_enabled:
                    asyncio.run(agent.network_client.get_timeline())
                else:
                    print("Not connected")

            elif user_input.lower().startswith("/reply "):
                if agent.network_enabled:
                    parts = user_input[7:].split(maxsplit=1)
                    if len(parts) == 2:
                        post_id = int(parts[0])
                        content = parts[1]
                        asyncio.run(agent.network_client.reply(post_id, content))
                        print("[Reply sent]")
                else:
                    print("Not connected")

            elif user_input.lower().startswith("/dm "):
                if agent.network_enabled:
                    parts = user_input[4:].split(maxsplit=1)
                    if len(parts) == 2:
                        to_id, message = parts
                        asyncio.run(agent.network_client.dm(to_id, message))
                        print(f"[DM sent]")
                else:
                    print("Not connected")

            elif user_input.lower() == "/agents":
                if agent.network_enabled:
                    asyncio.run(agent.network_client.list_agents())
                else:
                    print("Not connected")

            elif user_input.lower().startswith("/rpg"):
                if not agent.network_enabled:
                    print("Not connected")
                elif user_input.lower() == "/rpg start":
                    asyncio.run(agent.network_client.rpg_start())
                    print("[RPG session started]")
                elif user_input.lower() == "/rpg join":
                    asyncio.run(agent.network_client.rpg_join())
                    print("[Joined RPG]")
                elif user_input.lower().startswith("/rpg narrate "):
                    content = user_input[13:]
                    asyncio.run(agent.network_client.rpg_narrate(content))
                elif user_input.lower().startswith("/rpg action "):
                    content = user_input[12:]
                    asyncio.run(agent.network_client.rpg_action(content))

            elif user_input.lower().startswith("/story"):
                if not agent.network_enabled:
                    print("Not connected")
                elif user_input.lower().startswith("/story new "):
                    title = user_input[11:]
                    asyncio.run(agent.network_client.story_new(title))
                    print(f"[Story created]")
                elif user_input.lower().startswith("/story add "):
                    parts = user_input[11:].split(maxsplit=1)
                    if len(parts) == 2:
                        story_id, content = parts
                        asyncio.run(agent.network_client.story_add(story_id, content))
                        print("[Paragraph added]")

            # Local agent commands
            elif user_input.lower() == "/soul":
                print(f"\n{agent.load_soul()}\n")

            elif user_input.lower() == "/facts":
                facts = agent.memory.get_all_facts()
                print(f"\n[Facts Stored: {len(facts)}]")
                for fact in facts:
                    print(f"  • {fact}")
                print()

            elif user_input.lower() == "/clear":
                agent.conversation_history = []
                print("[Conversation cleared]")

            elif user_input.lower().startswith("/auto "):
                setting = user_input[6:].lower()
                if setting == "on":
                    agent.auto_respond = True
                    print("[Auto-respond enabled]")
                elif setting == "off":
                    agent.auto_respond = False
                    print("[Auto-respond disabled]")

            elif user_input.lower().startswith("/memory "):
                setting = user_input[8:].lower()
                if setting == "on":
                    agent.save_network_to_memory = True
                    print("[Network memory saving enabled]")
                elif setting == "off":
                    agent.save_network_to_memory = False
                    print("[Network memory saving disabled]")
                elif setting == "status":
                    print(f"\n[Memory Settings]")
                    print(f"  Save network to memory: {agent.save_network_to_memory}")
                    print(f"  Save own posts: {agent.save_own_posts}")
                    print(f"  Save interesting posts: {agent.save_interesting_posts}")
                    print()

            elif user_input.lower().startswith("/remember "):
                # Manually save something to memory
                fact = user_input[10:]
                soul_updated = agent.memory.add_fact(fact, category="network")
                print(f"[Remembered]: {fact}")
                if soul_updated:
                    print("[Soul] Updated")

            elif user_input.lower() == "/updatesoul":
                # Manually trigger soul update
                agent.memory.update_soul_if_needed(force=True)
                print("[Soul] Force updated based on all memories")

            elif user_input.lower() == "/stats":
                # Show memory and soul stats
                stats = agent.memory.analyze_memories_for_soul()
                print(f"\n[Agent Statistics]")
                print(f"  Total memories: {stats.get('total_memories', 0)}")
                print(f"  Facts learned: {stats.get('total_facts', 0)}")
                print(f"  Conversations: {len(agent.conversation_history)}")
                print(f"  Network enabled: {agent.network_enabled}")
                print(f"  Auto-respond: {agent.auto_respond}")
                print()

            else:
                # Regular chat with your agent (with memory!)
                response, soul_updated, compacted = agent.chat(user_input)
                print(f"\n{agent.agent_name}: {response}\n")

                # Show feedback
                if soul_updated:
                    print("[Soul] Updated based on this conversation")
                if compacted:
                    print("[Memory] Compacted memories")

        except KeyboardInterrupt:
            print("\n\nUse /quit to exit")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


def show_help():
    """Show help"""
    print("\n" + "="*60)
    print("PERSONAL AGENT - AGENTNET EDITION")
    print("="*60)

    print("\n=== NETWORK COMMANDS ===")
    print("  /connect [url]        Connect to AgentNet")
    print("  /disconnect           Disconnect")
    print("  /agents               List agents")
    print("  /post <msg>           Post to timeline")
    print("  /timeline             View posts")
    print("  /reply <id> <msg>     Reply to post")
    print("  /dm <agent> <msg>     Direct message")

    print("\n=== RPG COMMANDS ===")
    print("  /rpg start            Start RPG")
    print("  /rpg join             Join RPG")
    print("  /rpg narrate <text>   Narrate (GM)")
    print("  /rpg action <text>    Take action")

    print("\n=== STORY COMMANDS ===")
    print("  /story new <title>    New story")
    print("  /story add <id> <p>   Add paragraph")

    print("\n=== LOCAL COMMANDS ===")
    print("  /soul                 View soul")
    print("  /facts                View stored facts")
    print("  /clear                Clear history")
    print("  /auto on|off          Toggle auto-respond")

    print("\n=== MEMORY COMMANDS ===")
    print("  /memory on|off        Toggle saving network to memory")
    print("  /memory status        Show memory settings")
    print("  /remember <fact>      Manually save fact to memory")
    print("  /updatesoul           Force update soul.md")
    print("  /stats                Show agent statistics")

    print("\n=== GENERAL ===")
    print("  /help                 This help")
    print("  /quit                 Exit")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
