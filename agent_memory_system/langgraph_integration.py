"""
LangGraph Integration with Advanced Memory System
Demonstrates how to integrate the memory system with LangGraph workflows.
"""

from typing import Dict, Any, List, TypedDict
from langgraph.graph import Graph, END
from langgraph.prebuilt import ToolExecutor
import json
import time

from memory_system import LongShortTermMemory, MemoryType, MemoryPriority


class AgentState(TypedDict):
    """State for the agent workflow"""
    query: str
    memories: List[Any]
    response: str
    context: Dict[str, Any]
    user_id: str


class LangGraphMemoryAgent:
    """Agent with LangGraph workflow and integrated memory system"""
    
    def __init__(self):
        self.memory = LongShortTermMemory()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow with memory integration"""
        
        # Create the graph
        workflow = Graph()
        
        # Add nodes
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("process_query", self._process_query_node)
        workflow.add_node("store_interaction", self._store_interaction_node)
        workflow.add_node("learn_and_consolidate", self._learn_and_consolidate_node)
        
        # Define edges
        workflow.add_edge("retrieve_memory", "process_query")
        workflow.add_edge("process_query", "store_interaction")
        workflow.add_edge("store_interaction", "learn_and_consolidate")
        workflow.add_edge("learn_and_consolidate", END)
        
        # Set entry point
        workflow.set_entry_point("retrieve_memory")
        
        return workflow.compile()
    
    def _retrieve_memory_node(self, state: AgentState) -> AgentState:
        """Node to retrieve relevant memories"""
        query = state.get("query", "")
        user_id = state.get("user_id", "")
        context = state.get("context", {})
        
        # Add user context
        if user_id:
            context["user_id"] = user_id
        
        # Retrieve relevant memories
        memories = self.memory.retrieve_memories(
            query, 
            include_short_term=True,
            limit=10
        )
        
        print(f"🔍 Retrieved {len(memories)} memories for query: '{query}'")
        
        return {
            **state,
            "memories": memories,
            "context": context
        }
    
    def _process_query_node(self, state: AgentState) -> AgentState:
        """Node to process the query with memory context"""
        query = state.get("query", "")
        memories = state.get("memories", [])
        context = state.get("context", {})
        
        # Build context from memories
        memory_context = ""
        if memories:
            memory_context = "\nRelevant Context:\n"
            for i, memory in enumerate(memories, 1):
                memory_context += f"{i}. {memory.content}\n"
        
        # Process query with context (simplified example)
        response = self._generate_response(query, memory_context, context)
        
        print(f"💭 Generated response for query: '{query}'")
        
        return {
            **state,
            "response": response
        }
    
    def _store_interaction_node(self, state: AgentState) -> AgentState:
        """Node to store the interaction in memory"""
        query = state.get("query", "")
        response = state.get("response", "")
        user_id = state.get("user_id", "")
        
        # Store user message
        self.memory.add_memory(
            content=f"User query: {query}",
            memory_type=MemoryType.SHORT_TERM,
            priority=MemoryPriority.MEDIUM,
            context={'user_id': user_id, 'type': 'user_query'}
        )
        
        # Store agent response
        self.memory.add_memory(
            content=f"Agent response: {response}",
            memory_type=MemoryType.SHORT_TERM,
            priority=MemoryPriority.MEDIUM,
            context={'user_id': user_id, 'type': 'agent_response'}
        )
        
        print(f"💾 Stored interaction for user: {user_id}")
        
        return state
    
    def _learn_and_consolidate_node(self, state: AgentState) -> AgentState:
        """Node to learn from interaction and consolidate memories"""
        query = state.get("query", "")
        response = state.get("response", "")
        user_id = state.get("user_id", "")
        
        # Extract potential learning from interaction
        learning = self._extract_learning(query, response)
        if learning:
            self.memory.add_memory(
                content=f"Learned about {user_id}: {learning}",
                memory_type=MemoryType.LONG_TERM,
                priority=MemoryPriority.HIGH,
                tags=['learning', 'user_preference'],
                context={'user_id': user_id}
            )
            print(f"🧠 Learned: {learning}")
        
        # Periodically consolidate memories
        if len(self.memory.short_term_store.memories) > 50:
            self.memory.consolidate_memories()
            print("🔄 Consolidated memories")
        
        return state
    
    def _generate_response(self, query: str, memory_context: str, context: Dict[str, Any]) -> str:
        """Generate response using query and memory context (simplified)"""
        user_id = context.get("user_id", "Unknown")
        
        # Simple response generation logic
        if "name" in query.lower() and user_id != "Unknown":
            # Try to find user's name in memories
            user_memories = [m for m in self.memory.short_term_store.memories.values() 
                           if m.context.get('user_id') == user_id]
            
            for memory in user_memories:
                if "my name is" in memory.content.lower():
                    name = memory.content.split("my name is")[-1].strip().rstrip(".")
                    return f"Hello {name}! I remember your name from our previous conversation."
        
        # Generic response with memory context
        if memory_context:
            return f"I found some relevant information: {memory_context}\n\nRegarding your query '{query}', I can help you with that."
        else:
            return f"I don't have specific memories about '{query}', but I can still help you with general information."
    
    def _extract_learning(self, query: str, response: str) -> str:
        """Extract learning from interaction (simplified)"""
        # Simple pattern matching for learning extraction
        if "like" in query.lower() or "prefer" in query.lower():
            return query
        if "important" in query.lower():
            return query
        return None
    
    def process_query(self, query: str, user_id: str = "anonymous") -> str:
        """Process a query through the complete workflow"""
        initial_state = AgentState(
            query=query,
            memories=[],
            response="",
            context={},
            user_id=user_id
        )
        
        # Run the workflow
        result = self.workflow.invoke(initial_state)
        
        return result.get("response", "No response generated")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "short_term_count": len(self.memory.short_term_store.memories),
            "long_term_count": len(self.memory.long_term_store.memories),
            "current_session": self.memory.current_session
        }
    
    def save_memory(self, filepath: str):
        """Save memory state to file"""
        self.memory.save_to_file(filepath)
        print(f"💾 Memory saved to {filepath}")
    
    def load_memory(self, filepath: str):
        """Load memory state from file"""
        self.memory.load_from_file(filepath)
        print(f"📂 Memory loaded from {filepath}")


# Enhanced demonstration with LangGraph integration
def demo_langgraph_memory_agent():
    """Demonstrate the LangGraph memory agent"""
    print("=== LangGraph Memory Agent Demo ===\n")
    
    # Create agent
    agent = LangGraphMemoryAgent()
    
    # Simulate a conversation
    conversations = [
        ("Hello, my name is Bob", "user_bob"),
        ("I like Python programming", "user_bob"),
        ("What's my name?", "user_bob"),
        ("I'm working on a machine learning project", "user_bob"),
        ("What programming languages do I like?", "user_bob"),
        
        # Different user
        ("Hi, I'm Alice", "user_alice"),
        ("I prefer JavaScript over Python", "user_alice"),
        ("What's my name?", "user_alice"),
    ]
    
    print("🗨️  Starting conversations...\n")
    
    for query, user_id in conversations:
        print(f"User {user_id}: {query}")
        response = agent.process_query(query, user_id)
        print(f"Agent: {response}\n")
        time.sleep(0.5)  # Small delay for demo
    
    # Show memory statistics
    stats = agent.get_memory_stats()
    print("📊 Memory Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test memory retrieval
    print(f"\n🔍 Testing memory retrieval for user_bob:")
    bob_memories = agent.memory.retrieve_memories(
        "Bob Python", 
        context={'user_id': 'user_bob'},
        limit=5
    )
    
    for i, memory in enumerate(bob_memories, 1):
        print(f"  {i}. {memory.content}")
    
    # Save memory state
    agent.save_memory("langgraph_memory_demo.json")
    
    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    demo_langgraph_memory_agent()