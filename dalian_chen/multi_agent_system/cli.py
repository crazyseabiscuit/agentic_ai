#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User Interface - Command Line Interface
用户界面 - 命令行界面

This module provides a command-line interface for the multi-agent system.
"""

import asyncio
import json
import sys
import signal
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
from pathlib import Path

from .core_system import MultiAgentState, memory_manager, tool_registry
from .agents import CoordinatorAgent, ResearcherAgent, AnalystAgent, ExecutorAgent, ValidatorAgent
from .feedback_system import feedback_interface, feedback_learning_system
from .tools import register_all_tools

class MultiAgentCLI:
    """Command Line Interface for Multi-Agent System"""
    
    def __init__(self):
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.coordinator = None
        self.agents = {}
        self.running = True
        
        # Initialize tools
        register_all_tools()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n\nReceived signal {signum}, shutting down gracefully...")
        self.running = False
        sys.exit(0)
        
    async def initialize_system(self):
        """Initialize the multi-agent system"""
        print("Initializing Multi-Agent System...")
        print("=" * 50)
        
        # Create coordinator
        self.coordinator = CoordinatorAgent(self.session_id)
        
        # Create specialist agents
        researcher = ResearcherAgent(self.session_id)
        analyst = AnalystAgent(self.session_id)
        executor = ExecutorAgent(self.session_id)
        validator = ValidatorAgent(self.session_id)
        
        # Register agents with coordinator
        self.coordinator.register_agent(researcher)
        self.coordinator.register_agent(analyst)
        self.coordinator.register_agent(executor)
        self.coordinator.register_agent(validator)
        
        # Store agents
        self.agents = {
            "coordinator": self.coordinator,
            "researcher": researcher,
            "analyst": analyst,
            "executor": executor,
            "validator": validator
        }
        
        print("✓ Coordinator Agent created")
        print("✓ Researcher Agent created")
        print("✓ Analyst Agent created")
        print("✓ Executor Agent created")
        print("✓ Validator Agent created")
        print()
        
        # Show system status
        await self.show_system_status()
        
    async def show_system_status(self):
        """Display system status"""
        print("System Status:")
        print("-" * 30)
        print(f"Session ID: {self.session_id}")
        print(f"Active Agents: {len(self.agents)}")
        print(f"Registered Tools: {len(tool_registry.tools)}")
        print(f"Memory Database: {memory_manager.db_path}")
        print()
        
        # Show agent status
        print("Agent Status:")
        for name, agent in self.agents.items():
            status = "🟢 Active" if agent.state == "idle" else "🟡 Working" if agent.state == "working" else "🔴 Error"
            print(f"  {name.capitalize()}: {status}")
        print()
        
    async def show_help(self):
        """Show help information"""
        print("""
Multi-Agent System Commands:
============================

Basic Commands:
  help, h         - Show this help message
  status, s       - Show system status
  agents, a       - List all agents
  tools, t        - List available tools
  memory, m       - Show memory usage
  feedback, f     - Show feedback history
  clear, c        - Clear screen
  quit, q         - Exit the system

Interaction Commands:
  ask <question>  - Ask a question to the system
  task <task>     - Assign a task to the system
  research <topic>- Conduct research on a topic
  analyze <data>  - Analyze data
  validate <item> - Validate something

Agent Commands:
  agent <name> <command> - Send command to specific agent
  agent status           - Show agent status

Feedback Commands:
  feedback show          - Show feedback history
  feedback analyze       - Analyze feedback patterns
  feedback report        - Generate performance report

Examples:
  ask What is the current market trend?
  task Analyze the financial data for Q1 2024
  research artificial intelligence in healthcare
  agent researcher search for recent AI papers
  feedback analyze

Tips:
  - Use natural language for commands
  - The system will automatically route requests to appropriate agents
  - Feedback can be provided during key phases
  - All interactions are stored in memory for context
        """)
        
    async def list_agents(self):
        """List all agents and their capabilities"""
        print("Available Agents:")
        print("-" * 40)
        
        for name, agent in self.agents.items():
            print(f"\n{name.capitalize()} Agent:")
            print(f"  ID: {agent.agent_id}")
            print(f"  Type: {agent.config.agent_type.value}")
            print(f"  Status: {agent.state}")
            print(f"  Tools: {len(agent.tools)}")
            print(f"  Description: {agent.config.description}")
            
    async def list_tools(self):
        """List all available tools"""
        print("Available Tools:")
        print("-" * 40)
        
        categories = tool_registry.list_tools()
        for category, tools in categories.items():
            print(f"\n{category.upper()}:")
            for tool_name in tools:
                tool_info = tool_registry.tools.get(tool_name)
                if tool_info:
                    print(f"  • {tool_name}: {tool_info['description']}")
                    
    async def show_memory_status(self):
        """Show memory usage and status"""
        print("Memory Status:")
        print("-" * 30)
        
        # Get conversation history
        history = memory_manager.get_conversation_history(self.session_id)
        print(f"Conversation History: {len(history)} messages")
        
        # Get feedback history
        feedback = memory_manager.get_feedback_history()
        print(f"Feedback History: {len(feedback)} entries")
        
        # Show recent conversations
        if history:
            print("\nRecent Conversations:")
            for i, msg in enumerate(history[-5:]):
                print(f"  {i+1}. [{msg['role']}] {msg['content'][:50]}...")
                
    async def show_feedback_history(self):
        """Show feedback history"""
        print("Feedback History:")
        print("-" * 30)
        
        feedback = memory_manager.get_feedback_history()
        
        if not feedback:
            print("No feedback history available")
            return
            
        for i, fb in enumerate(feedback[-10:]):  # Show last 10
            print(f"\n{i+1}. {fb.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Agent: {fb.agent_id}")
            print(f"   Phase: {fb.phase}")
            print(f"   Type: {fb.feedback_type.value}")
            print(f"   Score: {fb.score}/10")
            print(f"   Comment: {fb.comment}")
            
    async def analyze_feedback(self):
        """Analyze feedback patterns"""
        print("Analyzing Feedback Patterns...")
        print("-" * 40)
        
        analysis = feedback_interface.analyze_feedback_patterns()
        
        if "message" in analysis:
            print(analysis["message"])
            return
            
        print(f"Total Feedback Count: {analysis['total_feedback_count']}")
        print(f"Average Score: {analysis['average_score']:.1f}/10")
        
        print("\nFeedback Type Distribution:")
        for ftype, count in analysis["feedback_type_distribution"].items():
            print(f"  {ftype}: {count}")
            
        print("\nPhase Performance:")
        for phase, score in analysis["phase_performance"].items():
            print(f"  {phase}: {score:.1f}/10")
            
        if analysis["improvement_areas"]:
            print("\nImprovement Areas:")
            for area in analysis["improvement_areas"]:
                print(f"  • {area}")
                
    async def generate_performance_report(self):
        """Generate performance report"""
        print("Generating Performance Report...")
        print("-" * 40)
        
        report = feedback_learning_system.generate_performance_report()
        print(report)
        
    async def process_user_input(self, user_input: str) -> str:
        """Process user input and return response"""
        try:
            # Add to memory
            memory_manager.add_message(self.session_id, "human", user_input)
            
            # Route to appropriate handler
            if user_input.startswith("ask "):
                question = user_input[4:].strip()
                return await self.coordinator.process_user_input(question)
            elif user_input.startswith("task "):
                task = user_input[5:].strip()
                return await self.coordinator.process_user_input(task)
            elif user_input.startswith("research "):
                topic = user_input[9:].strip()
                return await self.coordinator.process_user_input(f"Research: {topic}")
            elif user_input.startswith("analyze "):
                data = user_input[8:].strip()
                return await self.coordinator.process_user_input(f"Analyze: {data}")
            elif user_input.startswith("agent "):
                return await self.handle_agent_command(user_input[6:].strip())
            else:
                # Default to coordinator
                return await self.coordinator.process_user_input(user_input)
                
        except Exception as e:
            error_msg = f"Error processing input: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
            
    async def handle_agent_command(self, command: str) -> str:
        """Handle agent-specific commands"""
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            return "Please specify an agent and command"
            
        agent_name, agent_command = parts
        agent = self.agents.get(agent_name.lower())
        
        if not agent:
            return f"Agent '{agent_name}' not found"
            
        # Send command to agent
        from .core_system import Message
        import uuid
        
        message = Message(
            id=str(uuid.uuid4()),
            sender="user",
            receiver=agent.agent_id,
            content=agent_command,
            timestamp=datetime.now(),
            message_type="command"
        )
        
        await message_bus.publish(message)
        
        return f"Command sent to {agent_name} agent"
        
    async def interactive_loop(self):
        """Main interactive loop"""
        print("\n🤖 Multi-Agent System Ready!")
        print("Type 'help' for available commands or 'quit' to exit.")
        print("=" * 60)
        
        while self.running:
            try:
                # Get user input
                user_input = input(f"\n[{self.session_id}] > ").strip()
                
                if not user_input:
                    continue
                    
                # Handle special commands
                if user_input.lower() in ['quit', 'q', 'exit']:
                    print("Goodbye! 👋")
                    break
                elif user_input.lower() in ['help', 'h']:
                    await self.show_help()
                    continue
                elif user_input.lower() in ['status', 's']:
                    await self.show_system_status()
                    continue
                elif user_input.lower() in ['agents', 'a']:
                    await self.list_agents()
                    continue
                elif user_input.lower() in ['tools', 't']:
                    await self.list_tools()
                    continue
                elif user_input.lower() in ['memory', 'm']:
                    await self.show_memory_status()
                    continue
                elif user_input.lower() in ['feedback', 'f']:
                    await self.show_feedback_history()
                    continue
                elif user_input.lower() in ['clear', 'c']:
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                elif user_input.lower() == 'feedback analyze':
                    await self.analyze_feedback()
                    continue
                elif user_input.lower() == 'feedback report':
                    await self.generate_performance_report()
                    continue
                    
                # Process user input
                print("🔄 Processing...")
                response = await self.process_user_input(user_input)
                
                # Display response
                print("\n📝 Response:")
                print("-" * 40)
                print(response)
                print("-" * 40)
                
                # Check if feedback should be requested
                if len(user_input) > 20:  # For substantial inputs
                    should_request = input("\n🤔 Would you like to provide feedback on this response? (y/N): ").strip().lower()
                    if should_request == 'y':
                        feedback_interface.request_feedback(
                            self.session_id,
                            "coordinator",
                            "response",
                            response,
                            {"user_input": user_input}
                        )
                        
            except KeyboardInterrupt:
                print("\n\nInterrupt received. Type 'quit' to exit.")
            except EOFError:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                continue
                
    async def run_demo(self):
        """Run a demonstration of the system"""
        print("🎭 Running Multi-Agent System Demo...")
        print("=" * 50)
        
        demo_tasks = [
            "What is the current trend in artificial intelligence?",
            "Research the latest developments in quantum computing",
            "Analyze the potential impact of AI on financial markets",
            "Generate a comprehensive report on renewable energy investments"
        ]
        
        for i, task in enumerate(demo_tasks, 1):
            print(f"\n📋 Demo Task {i}/{len(demo_tasks)}")
            print(f"Task: {task}")
            print("-" * 40)
            
            print("🔄 Processing...")
            response = await self.coordinator.process_user_input(task)
            
            print("\n📝 Response:")
            print("-" * 40)
            print(response[:500] + "..." if len(response) > 500 else response)
            print("-" * 40)
            
            # Simulate feedback
            if i % 2 == 0:
                print("\n💭 Simulating feedback...")
                feedback_interface.request_feedback(
                    self.session_id,
                    "coordinator",
                    f"demo_task_{i}",
                    response,
                    {"demo": True}
                )
                
            if i < len(demo_tasks):
                input("\nPress Enter to continue to next demo task...")
                
        print("\n🎉 Demo completed!")
        await self.show_system_status()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Multi-Agent System CLI')
    parser.add_argument('--demo', action='store_true', help='Run demonstration mode')
    parser.add_argument('--session', type=str, help='Custom session ID')
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = MultiAgentCLI()
    
    if args.session:
        cli.session_id = args.session
        
    # Run the system
    async def run_system():
        await cli.initialize_system()
        
        if args.demo:
            await cli.run_demo()
        else:
            await cli.interactive_loop()
            
    try:
        asyncio.run(run_system())
    except KeyboardInterrupt:
        print("\n\nSystem shutdown complete.")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()