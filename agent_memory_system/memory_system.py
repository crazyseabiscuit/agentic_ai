"""
Advanced Long Short-Term Memory System for AI Agents
Based on LangGraph procedural memory concepts with enhanced capabilities.
UV-compatible implementation.
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
from abc import ABC, abstractmethod


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
    embedding: List[float] = None
    summary: str = None
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
        data = asdict(self)
        data['memory_type'] = self.memory_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        data['memory_type'] = MemoryType(data['memory_type'])
        data['priority'] = MemoryPriority(data['priority'])
        return cls(**data)


class MemoryStore(ABC):
    """Abstract base class for memory storage"""
    
    @abstractmethod
    def add(self, entry: MemoryEntry) -> bool:
        """Add a memory entry"""
        pass
    
    @abstractmethod
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID"""
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries"""
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry"""
        pass


class InMemoryStore(MemoryStore):
    """In-memory implementation of memory store"""
    
    def __init__(self):
        self.memories: Dict[str, MemoryEntry] = {}
        self.index: Dict[str, List[str]] = {}  # Simple keyword index
    
    def add(self, entry: MemoryEntry) -> bool:
        self.memories[entry.id] = entry
        self._update_index(entry)
        return True
    
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        entry = self.memories.get(memory_id)
        if entry:
            entry.access_count += 1
            entry.last_accessed = time.time()
        return entry
    
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        # Simple keyword-based search
        query_lower = query.lower()
        results = []
        
        for memory_id, entry in self.memories.items():
            if (query_lower in entry.content.lower() or 
                any(query_lower in tag.lower() for tag in entry.tags)):
                results.append(entry)
        
        # Sort by priority and access count
        results.sort(key=lambda x: (x.priority.value, x.access_count), reverse=True)
        return results[:limit]
    
    def delete(self, memory_id: str) -> bool:
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        return False
    
    def _update_index(self, entry: MemoryEntry):
        """Update search index with entry keywords"""
        words = entry.content.lower().split()
        for word in words:
            if word not in self.index:
                self.index[word] = []
            if entry.id not in self.index[word]:
                self.index[word].append(entry.id)


class MemorySummarizer:
    """Handles memory summarization and compression"""
    
    def __init__(self, max_length: int = 500):
        self.max_length = max_length
    
    def summarize(self, content: str) -> str:
        """Simple summarization logic (in real implementation, use LLM)"""
        if len(content) <= self.max_length:
            return content
        
        # Simple extractive summarization
        sentences = content.split('. ')
        if len(sentences) <= 2:
            return content
        
        # Return first and last sentences for now
        return f"{sentences[0]}. [...] {sentences[-1]}."
    
    def compress_memories(self, memories: List[MemoryEntry]) -> List[MemoryEntry]:
        """Compress multiple memories into fewer entries"""
        if len(memories) <= 3:
            return memories
        
        # Group by context and priority
        groups = {}
        for memory in memories:
            context_key = memory.context.get('session', 'default')
            if context_key not in groups:
                groups[context_key] = []
            groups[context_key].append(memory)
        
        compressed = []
        for context_key, group_memories in groups.items():
            if len(group_memories) > 3:
                # Create a summary memory
                combined_content = " | ".join([m.content for m in group_memories])
                summary_entry = MemoryEntry(
                    id=str(uuid.uuid4()),
                    content=f"Summary of {len(group_memories)} memories: {self.summarize(combined_content)}",
                    memory_type=MemoryType.LONG_TERM,
                    priority=MemoryPriority.MEDIUM,
                    timestamp=time.time(),
                    context={'session': context_key, 'compressed': True}
                )
                compressed.append(summary_entry)
                
                # Keep only the highest priority individual memories
                group_memories.sort(key=lambda x: x.priority.value, reverse=True)
                compressed.extend(group_memories[:2])
            else:
                compressed.extend(group_memories)
        
        return compressed


class MemoryRetriever:
    """Handles memory retrieval with relevance scoring"""
    
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
    
    def retrieve_relevant(self, query: str, context: Dict[str, Any] = None, 
                         limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories relevant to the query and context"""
        # Basic search
        candidates = self.memory_store.search(query, limit * 2)
        
        # Score based on relevance
        scored_memories = []
        for memory in candidates:
            score = self._calculate_relevance_score(query, memory, context)
            scored_memories.append((memory, score))
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in scored_memories[:limit]]
    
    def _calculate_relevance_score(self, query: str, memory: MemoryEntry, 
                                context: Dict[str, Any] = None) -> float:
        """Calculate relevance score for a memory"""
        score = 0.0
        
        # Content similarity (simple keyword matching)
        query_words = set(query.lower().split())
        content_words = set(memory.content.lower().split())
        word_overlap = len(query_words.intersection(content_words))
        score += word_overlap * 0.3
        
        # Priority boost
        score += memory.priority.value * 0.2
        
        # Recency boost
        age = time.time() - memory.timestamp
        recency_score = max(0, 1 - age / (30 * 24 * 60 * 60))  # 30 days decay
        score += recency_score * 0.2
        
        # Access frequency boost
        frequency_score = min(1, memory.access_count / 10)
        score += frequency_score * 0.1
        
        # Context matching
        if context and memory.context:
            context_match = sum(1 for k, v in context.items() 
                              if k in memory.context and memory.context[k] == v)
            score += context_match * 0.2
        
        return score


class LongShortTermMemory:
    """Main memory system combining long and short-term memory"""
    
    def __init__(self, short_term_capacity: int = 100, long_term_capacity: int = 1000):
        self.short_term_store = InMemoryStore()
        self.long_term_store = InMemoryStore()
        self.short_term_capacity = short_term_capacity
        self.long_term_capacity = long_term_capacity
        self.summarizer = MemorySummarizer()
        self.retriever = MemoryRetriever(self.long_term_store)
        self.current_session = str(uuid.uuid4())
    
    def add_memory(self, content: str, memory_type: MemoryType = MemoryType.SHORT_TERM,
                   priority: MemoryPriority = MemoryPriority.MEDIUM,
                   context: Dict[str, Any] = None, tags: List[str] = None) -> str:
        """Add a new memory entry"""
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            memory_type=memory_type,
            priority=priority,
            timestamp=time.time(),
            context=context or {'session': self.current_session},
            tags=tags or []
        )
        
        # Add to appropriate store
        if memory_type == MemoryType.SHORT_TERM:
            self.short_term_store.add(entry)
            self._manage_short_term_capacity()
        else:
            self.long_term_store.add(entry)
            self._manage_long_term_capacity()
        
        return entry.id
    
    def retrieve_memories(self, query: str, include_short_term: bool = True,
                         limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories relevant to the query"""
        memories = []
        
        # Get long-term memories
        long_term_memories = self.retriever.retrieve_relevant(query, limit=limit)
        memories.extend(long_term_memories)
        
        # Get short-term memories if requested
        if include_short_term:
            short_term_memories = self.short_term_store.search(query, limit=limit//2)
            memories.extend(short_term_memories)
        
        # Sort by relevance and return
        memories.sort(key=lambda x: (x.priority.value, x.access_count), reverse=True)
        return memories[:limit]
    
    def get_recent_memories(self, limit: int = 10) -> List[MemoryEntry]:
        """Get most recent memories"""
        all_memories = list(self.short_term_store.memories.values()) + \
                      list(self.long_term_store.memories.values())
        all_memories.sort(key=lambda x: x.timestamp, reverse=True)
        return all_memories[:limit]
    
    def consolidate_memories(self):
        """Consolidate short-term memories into long-term memory"""
        short_term_memories = list(self.short_term_store.memories.values())
        
        if len(short_term_memories) > self.short_term_capacity * 0.8:
            # Get oldest memories
            short_term_memories.sort(key=lambda x: x.timestamp)
            to_consolidate = short_term_memories[:int(self.short_term_capacity * 0.3)]
            
            # Compress and move to long-term
            compressed = self.summarizer.compress_memories(to_consolidate)
            for memory in compressed:
                memory.memory_type = MemoryType.LONG_TERM
                self.long_term_store.add(memory)
                self.short_term_store.delete(memory.id)
    
    def _manage_short_term_capacity(self):
        """Manage short-term memory capacity"""
        if len(self.short_term_store.memories) > self.short_term_capacity:
            # Remove oldest, lowest priority memories
            memories = list(self.short_term_store.memories.values())
            memories.sort(key=lambda x: (x.priority.value, x.timestamp))
            to_remove = memories[:len(memories) - self.short_term_capacity]
            for memory in to_remove:
                self.short_term_store.delete(memory.id)
    
    def _manage_long_term_capacity(self):
        """Manage long-term memory capacity"""
        if len(self.long_term_store.memories) > self.long_term_capacity:
            # Remove lowest priority, least accessed memories
            memories = list(self.long_term_store.memories.values())
            memories.sort(key=lambda x: (x.priority.value, x.access_count, x.timestamp))
            to_remove = memories[:len(memories) - self.long_term_capacity]
            for memory in to_remove:
                self.long_term_store.delete(memory.id)
    
    def save_to_file(self, filepath: str):
        """Save memory state to file"""
        data = {
            'short_term': [m.to_dict() for m in self.short_term_store.memories.values()],
            'long_term': [m.to_dict() for m in self.long_term_store.memories.values()],
            'current_session': self.current_session
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str):
        """Load memory state from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load memories
            for mem_data in data.get('short_term', []):
                self.short_term_store.add(MemoryEntry.from_dict(mem_data))
            
            for mem_data in data.get('long_term', []):
                self.long_term_store.add(MemoryEntry.from_dict(mem_data))
            
            self.current_session = data.get('current_session', str(uuid.uuid4()))
            
        except FileNotFoundError:
            print(f"No memory file found at {filepath}, starting with empty memory")


# Example usage and integration with agent
class AgentWithMemory:
    """Example agent with integrated memory system"""
    
    def __init__(self):
        self.memory = LongShortTermMemory()
        self.name = "MemoryAgent"
    
    def process_message(self, message: str, user_id: str = None) -> str:
        """Process a message with memory context"""
        # Retrieve relevant memories
        context_memories = self.memory.retrieve_memories(message, limit=5)
        
        # Build context string
        context = "\n".join([f"Memory: {mem.content}" for mem in context_memories])
        
        # Store the current message
        self.memory.add_memory(
            content=f"User said: {message}",
            memory_type=MemoryType.SHORT_TERM,
            priority=MemoryPriority.MEDIUM,
            context={'user_id': user_id, 'type': 'user_message'}
        )
        
        # Generate response (simplified)
        response = f"Processed: {message}. Context: {len(context_memories)} memories retrieved."
        
        # Store the response
        self.memory.add_memory(
            content=f"Agent responded: {response}",
            memory_type=MemoryType.SHORT_TERM,
            priority=MemoryPriority.MEDIUM,
            context={'user_id': user_id, 'type': 'agent_response'}
        )
        
        return response
    
    def learn_from_interaction(self, observation: str, learning: str):
        """Store important learnings in long-term memory"""
        self.memory.add_memory(
            content=f"Learned: {learning} from observation: {observation}",
            memory_type=MemoryType.LONG_TERM,
            priority=MemoryPriority.HIGH,
            tags=['learning', 'important']
        )
    
    def consolidate_periodically(self):
        """Periodically consolidate memories"""
        self.memory.consolidate_memories()


# Demonstration
if __name__ == "__main__":
    # Create agent with memory
    agent = AgentWithMemory()
    
    # Simulate conversation
    print("=== Agent Memory System Demo ===")
    
    # First interaction
    response1 = agent.process_message("Hello, my name is Alice", "user1")
    print(f"Response 1: {response1}")
    
    # Second interaction about the same topic
    response2 = agent.process_message("What's my name?", "user1")
    print(f"Response 2: {response2}")
    
    # Learn something important
    agent.learn_from_interaction(
        "User mentioned they like Python",
        "User Alice prefers Python programming"
    )
    
    # Test memory retrieval
    relevant_memories = agent.memory.retrieve_memories("Alice Python", limit=3)
    print(f"\nRetrieved {len(relevant_memories)} relevant memories:")
    for i, memory in enumerate(relevant_memories, 1):
        print(f"{i}. {memory.content} (Priority: {memory.priority.name})")
    
    # Show memory stats
    print(f"\nMemory Stats:")
    print(f"Short-term memories: {len(agent.memory.short_term_store.memories)}")
    print(f"Long-term memories: {len(agent.memory.long_term_store.memories)}")
    
    # Save memory state
    try:
        agent.memory.save_to_file("agent_memory.json")
        print("\nMemory saved to agent_memory.json")
    except Exception as e:
        print(f"\nFailed to save memory: {e}")