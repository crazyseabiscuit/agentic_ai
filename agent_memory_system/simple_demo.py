"""
Simplified Agent Memory System Demo
Standalone version without external dependencies for demonstration.
"""

import json
import time
from typing import Dict, Any, List, TypedDict
from dataclasses import dataclass
from enum import Enum


class MemoryType(Enum):
    """Types of memory entries"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryPriority(Enum):
    """Priority levels for memory entries"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryEntry:
    """Individual memory entry with metadata"""
    id: str
    content: str
    memory_type: MemoryType
    priority: MemoryPriority
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0
    context: Dict[str, Any] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.tags is None:
            self.tags = []
        if self.last_accessed == 0:
            self.last_accessed = self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = self.__dict__.copy()
        data['memory_type'] = self.memory_type.value
        data['priority'] = self.priority.value
        return data


class SimpleMemorySystem:
    """Simplified memory system for demonstration"""
    
    def __init__(self):
        self.short_term_memories = {}
        self.long_term_memories = {}
        self.session_id = f"session_{int(time.time())}"
    
    def add_memory(self, content: str, memory_type: MemoryType = MemoryType.SHORT_TERM,
                   priority: MemoryPriority = MemoryPriority.MEDIUM,
                   context: Dict[str, Any] = None, tags: List[str] = None) -> str:
        """Add a new memory entry"""
        memory_id = f"mem_{int(time.time() * 1000)}"
        
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            priority=priority,
            timestamp=time.time(),
            context=context or {},
            tags=tags or []
        )
        
        if memory_type == MemoryType.SHORT_TERM:
            self.short_term_memories[memory_id] = entry
        else:
            self.long_term_memories[memory_id] = entry
        
        return memory_id
    
    def search_memories(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by content"""
        query_lower = query.lower()
        results = []
        
        all_memories = {**self.short_term_memories, **self.long_term_memories}
        
        for memory in all_memories.values():
            if query_lower in memory.content.lower():
                results.append(memory)
        
        # Sort by priority and timestamp
        results.sort(key=lambda x: (x.priority.value, x.timestamp), reverse=True)
        return results[:limit]
    
    def get_user_memories(self, user_id: str) -> List[MemoryEntry]:
        """Get all memories for a specific user"""
        user_memories = []
        all_memories = {**self.short_term_memories, **self.long_term_memories}
        
        for memory in all_memories.values():
            if memory.context.get('user_id') == user_id:
                user_memories.append(memory)
        
        return user_memories
    
    def consolidate_memories(self):
        """Consolidate short-term memories to long-term"""
        if len(self.short_term_memories) > 5:  # Demo threshold
            # Move some short-term memories to long-term
            short_term_list = list(self.short_term_memories.values())
            short_term_list.sort(key=lambda x: x.timestamp)
            
            # Move oldest 2 memories to long-term
            for memory in short_term_list[:2]:
                memory.memory_type = MemoryType.LONG_TERM
                self.long_term_memories[memory.id] = memory
                del self.short_term_memories[memory.id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "short_term_count": len(self.short_term_memories),
            "long_term_count": len(self.long_term_memories),
            "total_count": len(self.short_term_memories) + len(self.long_term_memories),
            "session_id": self.session_id
        }
    
    def save_to_file(self, filepath: str):
        """Save memories to file"""
        data = {
            "short_term": [m.to_dict() for m in self.short_term_memories.values()],
            "long_term": [m.to_dict() for m in self.long_term_memories.values()],
            "session_id": self.session_id
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str):
        """Load memories from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load short-term memories
            for mem_data in data.get('short_term', []):
                mem_data['memory_type'] = MemoryType(mem_data['memory_type'])
                mem_data['priority'] = MemoryPriority(mem_data['priority'])
                entry = MemoryEntry(**mem_data)
                self.short_term_memories[entry.id] = entry
            
            # Load long-term memories
            for mem_data in data.get('long_term', []):
                mem_data['memory_type'] = MemoryType(mem_data['memory_type'])
                mem_data['priority'] = MemoryPriority(mem_data['priority'])
                entry = MemoryEntry(**mem_data)
                self.long_term_memories[entry.id] = entry
            
            self.session_id = data.get('session_id', self.session_id)
            
        except FileNotFoundError:
            print(f"No memory file found at {filepath}")


class SimpleMemoryAgent:
    """Simple agent with memory system"""
    
    def __init__(self):
        self.memory = SimpleMemorySystem()
        self.conversation_history = []
    
    def process_message(self, message: str, user_id: str = "anonymous") -> str:
        """Process a message with memory context"""
        # Search for relevant memories
        relevant_memories = self.memory.search_memories(message, limit=3)
        
        # Store the user message
        self.memory.add_memory(
            content=f"User: {message}",
            memory_type=MemoryType.SHORT_TERM,
            priority=MemoryPriority.MEDIUM,
            context={'user_id': user_id, 'type': 'user_message'}
        )
        
        # Generate response based on context
        response = self._generate_response(message, relevant_memories, user_id)
        
        # Store the response
        self.memory.add_memory(
            content=f"Agent: {response}",
            memory_type=MemoryType.SHORT_TERM,
            priority=MemoryPriority.MEDIUM,
            context={'user_id': user_id, 'type': 'agent_response'}
        )
        
        # Consolidate memories if needed
        self.memory.consolidate_memories()
        
        return response
    
    def _generate_response(self, message: str, relevant_memories: List[MemoryEntry], user_id: str) -> str:
        """Generate response based on message and memory context"""
        
        # Check if user is introducing themselves
        if "my name is" in message.lower():
            name = message.split("my name is")[-1].strip().rstrip(".")
            return f"Nice to meet you, {name}! I'll remember your name."
        
        # Check if user is asking about their name
        if "what's my name" in message.lower() or "do you remember my name" in message.lower():
            user_memories = self.memory.get_user_memories(user_id)
            for memory in user_memories:
                if "my name is" in memory.content.lower():
                    name = memory.content.split("my name is")[-1].strip().rstrip(".")
                    return f"Yes, I remember! Your name is {name}."
            return "I don't think you've told me your name yet."
        
        # Check if user is stating preferences
        if "i like" in message.lower() or "i prefer" in message.lower() or "i enjoy" in message.lower():
            # Store this as a long-term memory
            self.memory.add_memory(
                content=f"User preference: {message}",
                memory_type=MemoryType.LONG_TERM,
                priority=MemoryPriority.HIGH,
                context={'user_id': user_id, 'type': 'preference'},
                tags=['preference', 'user']
            )
            return f"I'll remember that you {message.lower().replace('i ', '')}!"
        
        # Check if user is asking about preferences
        if "what do i like" in message.lower() or "what are my preferences" in message.lower():
            user_memories = self.memory.get_user_memories(user_id)
            preferences = [m.content.replace("User preference: ", "") for m in user_memories if m.context.get('type') == 'preference']
            
            if preferences:
                return f"Based on our conversations, you've mentioned: {', '.join(preferences)}"
            else:
                return "I don't have any recorded preferences for you yet."
        
        # Generic response with memory context
        if relevant_memories:
            context_info = f" (I found {len(relevant_memories)} relevant memories)"
            return f"I understand your message about '{message}'{context_info}. How can I help you further?"
        else:
            return f"I hear you saying '{message}'. This is the first time we've discussed this topic."
    
    def get_memory_summary(self, user_id: str = None) -> str:
        """Get a summary of memories"""
        if user_id:
            user_memories = self.memory.get_user_memories(user_id)
            return f"User {user_id} has {len(user_memories)} memories stored."
        else:
            stats = self.memory.get_stats()
            return f"Memory system has {stats['total_count']} total memories ({stats['short_term_count']} short-term, {stats['long_term_count']} long-term)."


def demo_simple_memory_agent():
    """Demonstrate the simple memory agent"""
    print("=== Simple Memory Agent Demo ===\n")
    
    agent = SimpleMemoryAgent()
    
    # Simulate conversations
    conversations = [
        ("Hello, my name is Charlie", "user_charlie"),
        ("I like playing chess", "user_charlie"),
        ("What's my name?", "user_charlie"),
        ("I enjoy reading science fiction books", "user_charlie"),
        ("What do I like?", "user_charlie"),
        
        # Different user
        ("Hi, I'm Diana", "user_diana"),
        ("I prefer painting over drawing", "user_diana"),
        ("What's my name?", "user_diana"),
        ("What are my preferences?", "user_diana"),
        
        # More interactions with first user
        ("I also like programming in Python", "user_charlie"),
        ("What do I like to do?", "user_charlie"),
    ]
    
    print("🗨️  Starting conversations...\n")
    
    for i, (message, user_id) in enumerate(conversations, 1):
        print(f"Turn {i}:")
        print(f"  User {user_id}: {message}")
        response = agent.process_message(message, user_id)
        print(f"  Agent: {response}")
        print()
        time.sleep(0.3)  # Small delay for demo
    
    # Show memory statistics
    print("📊 Memory Statistics:")
    stats = agent.memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    # Show user-specific memory summaries
    print("👥 User Memory Summaries:")
    for user_id in ["user_charlie", "user_diana"]:
        summary = agent.get_memory_summary(user_id)
        print(f"  {summary}")
    print()
    
    # Show all memories for a user
    print("🧠 All memories for user_charlie:")
    charlie_memories = agent.memory.get_user_memories("user_charlie")
    for i, memory in enumerate(charlie_memories, 1):
        print(f"  {i}. [{memory.memory_type.value}] {memory.content}")
    print()
    
    # Test memory search
    print("🔍 Testing memory search for 'Python':")
    python_memories = agent.memory.search_memories("Python", limit=5)
    for i, memory in enumerate(python_memories, 1):
        print(f"  {i}. {memory.content}")
    print()
    
    # Save memory state
    agent.memory.save_to_file("simple_memory_demo.json")
    print("💾 Memory saved to simple_memory_demo.json")
    
    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    demo_simple_memory_agent()