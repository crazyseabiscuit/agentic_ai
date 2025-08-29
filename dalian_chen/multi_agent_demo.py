#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-Agent System Demo - Comprehensive Example
多智能体系统演示 - 综合示例

This script demonstrates the full capabilities of the multi-agent system including:
- Memory management
- Tool integration
- Human feedback
- Agent coordination
- RAGAS validation
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the multi_agent_system to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi_agent_system'))

from multi_agent_system.cli import MultiAgentCLI
from multi_agent_system.core_system import memory_manager, tool_registry, message_bus
from multi_agent_system.feedback_system import feedback_interface, feedback_learning_system, AutoFeedbackCollector
from multi_agent_system.agents import CoordinatorAgent, ResearcherAgent, AnalystAgent, ExecutorAgent, ValidatorAgent

class MultiAgentDemo:
    """Comprehensive demo of the multi-agent system"""
    
    def __init__(self):
        self.cli = MultiAgentCLI()
        self.auto_feedback = AutoFeedbackCollector()
        self.demo_results = {}
        
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration"""
        print("🎭 Multi-Agent System Comprehensive Demo")
        print("=" * 60)
        
        # Initialize system
        await self.cli.initialize_system()
        
        # Demo scenarios
        scenarios = [
            {
                "name": "Investment Research",
                "description": "Research investment opportunities and generate analysis",
                "tasks": [
                    "Research current market trends in technology sector",
                    "Analyze growth potential of AI companies",
                    "Generate investment recommendations"
                ]
            },
            {
                "name": "Financial Analysis",
                "description": "Comprehensive financial data analysis",
                "tasks": [
                    "Analyze portfolio performance metrics",
                    "Assess risk factors in current investments",
                    "Create diversification strategy"
                ]
            },
            {
                "name": "Market Intelligence",
                "description": "Market research and competitive analysis",
                "tasks": [
                    "Research competitive landscape in fintech",
                    "Analyze market entry opportunities",
                    "Generate strategic recommendations"
                ]
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['name']}")
            print(f"Description: {scenario['description']}")
            print("-" * 50)
            
            await self.run_scenario(scenario, i)
            
            # Generate feedback for demo
            await self.generate_demo_feedback(scenario['name'])
            
            if i < len(scenarios):
                input("\nPress Enter to continue to next scenario...")
        
        # Final analysis and reporting
        await self.generate_final_report()
        
    async def run_scenario(self, scenario: Dict, scenario_id: int):
        """Run a specific scenario"""
        print(f"\n🚀 Starting {scenario['name']}...")
        
        scenario_results = {
            "scenario_id": scenario_id,
            "name": scenario['name'],
            "tasks": [],
            "start_time": datetime.now().isoformat(),
            "responses": []
        }
        
        for j, task in enumerate(scenario['tasks'], 1):
            print(f"\n📝 Task {j}: {task}")
            print("-" * 40)
            
            # Process task through coordinator
            try:
                response = await self.cli.coordinator.process_user_input(task)
                
                # Store response
                scenario_results["responses"].append({
                    "task": task,
                    "response": response[:500] + "..." if len(response) > 500 else response,
                    "timestamp": datetime.now().isoformat()
                })
                
                print("📊 Response Summary:")
                print(f"Length: {len(response)} characters")
                print(f"Preview: {response[:200]}...")
                
            except Exception as e:
                print(f"❌ Error processing task: {str(e)}")
                scenario_results["responses"].append({
                    "task": task,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        scenario_results["end_time"] = datetime.now().isoformat()
        self.demo_results[f"scenario_{scenario_id}"] = scenario_results
        
    async def generate_demo_feedback(self, scenario_name: str):
        """Generate demo feedback for the scenario"""
        print(f"\n💭 Generating demo feedback for {scenario_name}...")
        
        # Simulate different performance levels
        feedback_data = self.auto_feedback.run_feedback_simulation(
            agent_id="coordinator",
            phases=["planning", "research", "analysis", "execution"],
            performance_levels=["high_performance", "medium_performance", "low_performance", "medium_performance"]
        )
        
        print(f"Generated {len(feedback_data)} feedback entries")
        
        # Analyze feedback patterns
        analysis = feedback_interface.analyze_feedback_patterns()
        if "message" not in analysis:
            print(f"Average Score: {analysis['average_score']:.1f}/10")
            print(f"Feedback Types: {analysis['feedback_type_distribution']}")
        
    async def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n📊 Generating Final Demo Report...")
        print("=" * 60)
        
        # System status
        print("\n🔧 System Status:")
        print(f"Active Agents: {len(self.cli.agents)}")
        print(f"Registered Tools: {len(tool_registry.tools)}")
        print(f"Memory Usage: {len(memory_manager.get_conversation_history('demo'))} conversations")
        
        # Performance report from feedback system
        print("\n📈 Performance Report:")
        performance_report = feedback_learning_system.generate_performance_report()
        print(performance_report)
        
        # Demo results summary
        print("\n🎯 Demo Results Summary:")
        for scenario_id, results in self.demo_results.items():
            print(f"\n{scenario_id}: {results['name']}")
            print(f"  Tasks: {len(results['responses'])}")
            print(f"  Duration: {results['start_time']} to {results['end_time']}")
            successful_tasks = sum(1 for r in results['responses'] if 'error' not in r)
            print(f"  Success Rate: {successful_tasks}/{len(results['responses'])} ({successful_tasks/len(results['responses'])*100:.1f}%)")
        
        # Memory analysis
        print("\n🧠 Memory Analysis:")
        all_conversations = memory_manager.get_conversation_history('demo')
        print(f"Total Conversations: {len(all_conversations)}")
        
        feedback_history = memory_manager.get_feedback_history()
        print(f"Total Feedback Entries: {len(feedback_history)}")
        
        # Tool usage statistics
        print("\n🛠️ Tool Usage Statistics:")
        for tool_name, tool_info in tool_registry.tools.items():
            if tool_info['usage_count'] > 0:
                print(f"  {tool_name}: {tool_info['usage_count']} uses")
        
        print("\n🎉 Demo Completed Successfully!")
        print("=" * 60)
        
    async def run_interactive_demo(self):
        """Run interactive demo with user participation"""
        print("🎮 Interactive Multi-Agent System Demo")
        print("=" * 50)
        
        # Initialize system
        await self.cli.initialize_system()
        
        print("\n💡 Interactive Demo Commands:")
        print("1. 'research <topic>' - Research a topic")
        print("2. 'analyze <data>' - Analyze data")
        print("3. 'task <description>' - Execute a task")
        print("4. 'status' - Show system status")
        print("5. 'feedback' - Show feedback history")
        print("6. 'quit' - Exit demo")
        
        await self.cli.interactive_loop()
        
    async def run_stress_test(self):
        """Run stress test to evaluate system performance"""
        print("🔥 Multi-Agent System Stress Test")
        print("=" * 50)
        
        await self.cli.initialize_system()
        
        # Generate multiple concurrent tasks
        stress_tasks = [
            "Anzeige die aktuellen Markttrends",
            "Research quantum computing developments",
            "Analyze cryptocurrency market",
            "Generate financial projections",
            "Research renewable energy investments",
            "Analyze global economic indicators",
            "Research artificial intelligence applications",
            "Analyze stock market performance",
            "Research biotechnology sector",
            "Analyze real estate market trends"
        ]
        
        print(f"🚀 Executing {len(stress_tasks)} concurrent tasks...")
        
        start_time = datetime.now()
        results = []
        
        for i, task in enumerate(stress_tasks, 1):
            print(f"\n⚡ Task {i}/{len(stress_tasks)}: {task[:50]}...")
            
            try:
                response = await self.cli.coordinator.process_user_input(task)
                results.append({
                    "task": task,
                    "success": True,
                    "response_length": len(response),
                    "timestamp": datetime.now().isoformat()
                })
                print(f"✅ Completed ({len(response)} chars)")
            except Exception as e:
                results.append({
                    "task": task,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                print(f"❌ Failed: {str(e)}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Stress test results
        print("\n📊 Stress Test Results:")
        print(f"Total Tasks: {len(stress_tasks)}")
        print(f"Successful: {sum(1 for r in results if r['success'])}")
        print(f"Failed: {sum(1 for r in results if not r['success'])}")
        print(f"Total Duration: {duration:.2f} seconds")
        print(f"Average Time per Task: {duration/len(stress_tasks):.2f} seconds")
        print(f"Success Rate: {sum(1 for r in results if r['success'])/len(results)*100:.1f}%")
        
        # Performance by task type
        print("\n📈 Performance Analysis:")
        successful_tasks = [r for r in results if r['success']]
        if successful_tasks:
            avg_response_length = sum(r['response_length'] for r in successful_tasks) / len(successful_tasks)
            print(f"Average Response Length: {avg_response_length:.0f} characters")

async def main():
    """Main demo function"""
    demo = MultiAgentDemo()
    
    print("🎭 Multi-Agent System Demo Suite")
    print("=" * 60)
    print("Choose demo mode:")
    print("1. Comprehensive Demo (Recommended)")
    print("2. Interactive Demo")
    print("3. Stress Test")
    print("4. Exit")
    
    try:
        choice = input("\nSelect mode (1-4): ").strip()
        
        if choice == "1":
            await demo.run_comprehensive_demo()
        elif choice == "2":
            await demo.run_interactive_demo()
        elif choice == "3":
            await demo.run_stress_test()
        elif choice == "4":
            print("Goodbye! 👋")
        else:
            print("Invalid choice. Running comprehensive demo...")
            await demo.run_comprehensive_demo()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())