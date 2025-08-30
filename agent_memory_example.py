```python
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

# --- Mock External Systems (for simulation purposes) ---
class MockLLM:
    """Simulates an LLM call."""
    def __call__(self, prompt: str, context: str = "") -> str:
        # In a real scenario, this would call an actual LLM API.
        # Here we simulate a response.
        if "generate a report" in prompt.lower():
            return "The Q2 sales report shows a 10% increase compared to Q1. Key drivers were product A and region X."
        elif "summarize the last interaction" in prompt.lower():
            return "The user asked for a sales report. I generated one based on the Q2 data."
        elif "reflect on the last task" in prompt.lower():
            return "The task was completed successfully. The report was accurate and relevant. No changes to procedure are needed."
        else:
            return f"Response to: {prompt}"

class MockRAGSystem:
    """Simulates a Retrieval-Augmented Generation system."""
    def query(self, question: str) -> str:
        # Simulate retrieving factual information.
        if "q2 sales data" in question.lower():
            return "Q2 Sales Data: Product A: $1.2M, Product B: $0.8M, Region X: $1.5M, Region Y: $0.5M"
        elif "company mission" in question.lower():
            return "Our mission is to deliver innovative solutions that empower our customers."
        else:
            return "No specific data found for the query."

class MockDatabase:
    """Simulates a database for long-term memory storage."""
    def __init__(self):
        self.episodic_memory: List[Dict[str, Any]] = []
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.procedural_memory: Dict[str, str] = {
            "generate_report_base_prompt": "You are an AI assistant. Your task is to generate a report based on the provided data. Be concise and factual.",
            "summarize_interaction_base_prompt": "You are an AI assistant. Summarize the key points of the last interaction.",
            "reflect_on_task_base_prompt": "You are an AI assistant. Reflect on the last task you performed. Was it successful? Should any procedures be updated?"
        }

    def store_interaction(self, interaction: Dict[str, Any]):
        self.episodic_memory.append(interaction)

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        return self.user_profiles.get(user_id, {})

    def update_user_profile(self, user_id: str, profile_update: Dict[str, Any]):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        self.user_profiles[user_id].update(profile_update)

    def get_procedural_memory(self, key: str) -> str:
        return self.procedural_memory.get(key, "")

    def update_procedural_memory(self, key: str, new_value: str):
        self.procedural_memory[key] = new_value

    def search_episodic_memory(self, user_id: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Simple search for demo purposes
        results = [entry for entry in self.episodic_memory if entry.get("user_id") == user_id and query.lower() in json.dumps(entry).lower()]
        return results[-limit:] # Return most recent matches

# --- Core Memory Components ---
@dataclass
class ShortTermMemory:
    """Represents the agent's working memory for the current interaction."""
    context_window: List[str] # Stores the conversation history
    current_state: Dict[str, Any] # Stores temporary variables and intermediate results

    def add_to_context(self, message: str):
        self.context_window.append(message)

    def update_state(self, key: str, value: Any):
        self.current_state[key] = value

    def get_state(self, key: str) -> Any:
        return self.current_state.get(key)

@dataclass
class LongTermMemory:
    """Manages the agent's persistent memory across interactions."""
    db: MockDatabase
    user_id: str

    def store_interaction(self, interaction_data: Dict[str, Any]):
        interaction_data["user_id"] = self.user_id
        interaction_data["timestamp"] = datetime.now().isoformat()
        self.db.store_interaction(interaction_data)

    def get_user_profile(self) -> Dict[str, Any]:
        return self.db.get_user_profile(self.user_id)

    def update_user_profile(self, profile_update: Dict[str, Any]):
        self.db.update_user_profile(self.user_id, profile_update)

    def get_procedural_rule(self, key: str) -> str:
        return self.db.get_procedural_memory(key)

    def update_procedural_rule(self, key: str, new_rule: str):
        self.db.update_procedural_memory(key, new_rule)

    def search_past_interactions(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        return self.db.search_episodic_memory(self.user_id, query, limit)

# --- The Agent ---
class AI_Agent:
    def __init__(self, user_id: str):
        self.llm = MockLLM()
        self.rag = MockRAGSystem()
        self.db = MockDatabase() # This would be a real DB connection in practice
        self.user_id = user_id
        self.short_term_memory = ShortTermMemory(context_window=[], current_state={})
        self.long_term_memory = LongTermMemory(self.db, self.user_id)

    def perceive(self, user_input: str):
        """Receives and processes user input."""
        self.short_term_memory.add_to_context(f"User: {user_input}")
        print(f"[Perception] Received input: {user_input}")

    def retrieve_relevant_memory(self):
        """Retrieves relevant information from long-term memory."""
        user_profile = self.long_term_memory.get_user_profile()
        # Example: Use user preference to guide RAG query
        preferred_detail_level = user_profile.get("preferred_detail_level", "summary")

        # Retrieve episodic memory related to the current context (simplified)
        # In a full implementation, this would be more sophisticated.
        last_query = self.short_term_memory.context_window[-1].replace("User: ", "") if self.short_term_memory.context_window else ""
        past_interactions = self.long_term_memory.search_past_interactions(last_query)

        # Retrieve semantic knowledge
        # This could be based on the user input or the current state.
        semantic_info = self.rag.query(f"Q2 sales data") # Example query

        # Store retrieved info in short-term memory for immediate use
        self.short_term_memory.update_state("user_profile", user_profile)
        self.short_term_memory.update_state("past_interactions", past_interactions)
        self.short_term_memory.update_state("semantic_info", semantic_info)
        self.short_term_memory.update_state("preferred_detail_level", preferred_detail_level)

        print(f"[Memory Retrieval] Found user profile: {user_profile}")
        print(f"[Memory Retrieval] Found past interactions: {len(past_interactions)} relevant")
        print(f"[Memory Retrieval] Retrieved semantic info: {semantic_info[:50]}...") # Truncate for brevity

    def plan_and_execute(self):
        """Plans the next action and executes it."""
        # Get the base procedural rule
        base_prompt = self.long_term_memory.get_procedural_rule("generate_report_base_prompt")
        semantic_info = self.short_term_memory.get_state("semantic_info")
        preferred_detail_level = self.short_term_memory.get_state("preferred_detail_level")

        # Construct the full prompt for the LLM
        full_prompt = f"{base_prompt}\n\nData: {semantic_info}\nDetail Level: {preferred_detail_level}"

        # Simulate LLM call
        response = self.llm(full_prompt)
        self.short_term_memory.add_to_context(f"Agent: {response}")
        self.short_term_memory.update_state("last_response", response)

        print(f"[Planning & Execution] Executed task. LLM Response: {response}")

        # Log the action taken
        self.short_term_memory.update_state("last_action", "generate_report")

    def reflect_and_learn(self):
        """Reflects on the interaction and updates long-term memory."""
        last_action = self.short_term_memory.get_state("last_action")
        last_response = self.short_term_memory.get_state("last_response")
        user_profile = self.short_term_memory.get_state("user_profile")

        if last_action == "generate_report":
            # 1. Store the interaction in Episodic Memory
            interaction_log = {
                "input": self.short_term_memory.context_window[0].replace("User: ", ""), # Simplified
                "action": last_action,
                "data_used": self.short_term_memory.get_state("semantic_info"),
                "response": last_response,
                # Outcome could be gathered from user feedback in a real system
                "outcome": "success" 
            }
            self.long_term_memory.store_interaction(interaction_log)
            print(f"[Reflection] Stored interaction in episodic memory.")

            # 2. Simulate reflecting on the task performance (Procedural Memory update)
            # This is a simplified example. In reality, this could be a more complex LLM call.
            reflect_prompt = self.long_term_memory.get_procedural_rule("reflect_on_task_base_prompt")
            reflection = self.llm(reflect_prompt)
            print(f"[Reflection] Self-reflection: {reflection}")

            # For this example, let's assume the reflection leads to a minor prompt refinement
            # based on the user's preferred detail level.
            if user_profile.get("preferred_detail_level") == "detailed":
                current_prompt = self.long_term_memory.get_procedural_rule("generate_report_base_prompt")
                if "concise" in current_prompt:
                    new_prompt = current_prompt.replace("concise", "detailed")
                    self.long_term_memory.update_procedural_rule("generate_report_base_prompt", new_prompt)
                    print(f"[Learning] Updated procedural memory rule for report generation.")

            # 3. Update User Profile (Episodic Learning)
            # Example: If this is the first interaction, set a default preference.
            if not user_profile:
                self.long_term_memory.update_user_profile({"preferred_detail_level": "summary"})
                print(f"[Learning] Initialized user profile.")

    def respond(self) -> str:
        """Generates the final response to the user."""
        # The response is already in the context window
        last_message = self.short_term_memory.context_window[-1]
        if last_message.startswith("Agent: "):
            response = last_message[7:] # Remove "Agent: " prefix
        else:
            # Fallback, should not happen in this simple flow
            response = "I have completed the task."
        print(f"[Response] Sending response to user.")
        return response

    def run(self, user_input: str) -> str:
        """Main execution flow of the agent."""
        print("\n--- Agent Cycle Start ---")
        self.perceive(user_input)
        self.retrieve_relevant_memory()
        self.plan_and_execute()
        self.reflect_and_learn()
        response = self.respond()
        print("--- Agent Cycle End ---\n")
        return response

# --- Example Usage ---
if __name__ == "__main__":
    # Simulate a user
    user_id = "user_123"
    agent = AI_Agent(user_id)

    # First interaction
    user_query_1 = "Can you generate a report on Q2 sales?"
    final_response_1 = agent.run(user_query_1)
    print(f"Final Response 1: {final_response_1}\n")

    # Second interaction, potentially building on the first
    user_query_2 = "Can you summarize our last interaction?"
    final_response_2 = agent.run(user_query_2)
    print(f"Final Response 2: {final_response_2}\n")

    # Show the state of long-term memory after interactions
    print("--- Long-Term Memory State After Interactions ---")
    print("User Profile:", agent.long_term_memory.get_user_profile())
    print("Stored Interactions Count:", len(agent.db.episodic_memory))
    print("Procedural Rule (generate_report):", agent.long_term_memory.get_procedural_rule("generate_report_base_prompt"))
```