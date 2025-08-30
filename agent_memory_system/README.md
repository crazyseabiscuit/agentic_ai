# Agent Memory System

A sophisticated long short-term memory system for AI agents, inspired by LangGraph's procedural memory concepts.

## Features

- **Dual Memory Architecture**: Short-term and long-term memory stores
- **Memory Types**: Support for different memory types (episodic, semantic, procedural)
- **Priority System**: Memory prioritization with automatic management
- **Relevance Scoring**: Intelligent memory retrieval based on multiple factors
- **Memory Compression**: Automatic summarization and consolidation
- **Persistence**: Save/load memory state to/from files
- **Context-Aware**: Memory retrieval with context matching

## Installation

```bash
# Create a new environment with UV
uv venv
uv pip install -e .

# Or install dependencies directly
uv pip install langgraph langchain numpy pydantic tiktoken
```

## Quick Start

```python
from memory_system import AgentWithMemory, MemoryType, MemoryPriority

# Create agent with memory
agent = AgentWithMemory()

# Process messages
response = agent.process_message("Hello, my name is Alice", "user1")
print(response)

# Learn important information
agent.learn_from_interaction(
    "User mentioned preferences",
    "User Alice prefers Python programming"
)

# Retrieve relevant memories
memories = agent.memory.retrieve_memories("Alice Python", limit=5)
for memory in memories:
    print(f"Memory: {memory.content}")
```

## Architecture

### Core Components

1. **MemoryEntry**: Individual memory with metadata
2. **MemoryStore**: Abstract storage interface
3. **InMemoryStore**: In-memory implementation
4. **MemorySummarizer**: Handles memory compression
5. **MemoryRetriever**: Intelligent memory retrieval
6. **LongShortTermMemory**: Main memory system

### Memory Types

- **SHORT_TERM**: Temporary, recent interactions
- **LONG_TERM**: Persistent, important information
- **WORKING**: Current task context
- **EPISODIC**: Event-based memories
- **SEMANTIC**: General knowledge
- **PROCEDURAL**: How-to knowledge

### Priority Levels

- **LOW**: Basic information
- **MEDIUM**: Normal interactions
- **HIGH**: Important learnings
- **CRITICAL**: Critical information

## Advanced Usage

### Custom Memory Management

```python
from memory_system import LongShortTermMemory, MemoryType, MemoryPriority

# Create custom memory system
memory = LongShortTermMemory(
    short_term_capacity=200,
    long_term_capacity=2000
)

# Add memories with custom properties
memory.add_memory(
    content="Important project deadline next week",
    memory_type=MemoryType.LONG_TERM,
    priority=MemoryPriority.HIGH,
    tags=['project', 'deadline'],
    context={'project_id': '123', 'user_id': 'alice'}
)

# Retrieve with context
relevant_memories = memory.retrieve_memories(
    "project deadline",
    context={'user_id': 'alice'},
    limit=10
)
```

### Memory Persistence

```python
# Save memory state
memory.save_to_file("my_memory.json")

# Load memory state
memory.load_from_file("my_memory.json")
```

### Memory Consolidation

```python
# Manually trigger memory consolidation
memory.consolidate_memories()

# Periodic consolidation in agent
agent.consolidate_periodically()
```

## Integration with LangGraph

The memory system can be integrated with LangGraph workflows:

```python
from langgraph.graph import Graph, END
from memory_system import LongShortTermMemory

# Create memory system
memory = LongShortTermMemory()

def memory_node(state):
    """Node that retrieves relevant memories"""
    query = state.get("query", "")
    memories = memory.retrieve_memories(query)
    return {**state, "memories": memories}

def process_node(state):
    """Node that processes with memory context"""
    memories = state.get("memories", [])
    context = "\n".join([m.content for m in memories])
    # Process with context...
    return state

# Build graph
workflow = Graph()
workflow.add_node("memory", memory_node)
workflow.add_node("process", process_node)
workflow.add_edge("memory", "process")
workflow.add_edge("process", END)

workflow.set_entry_point("memory")
app = workflow.compile()
```

## Configuration

The system can be configured through:

- **Capacity**: Set short-term and long-term memory limits
- **Summarization**: Configure memory compression parameters
- **Retrieval**: Customize relevance scoring weights
- **Persistence**: Choose storage backend

## Testing

```bash
# Run tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=memory_system
```

## License

MIT License