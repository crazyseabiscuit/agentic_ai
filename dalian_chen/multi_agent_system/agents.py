#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-Agent Implementation - Core Agent Classes
多智能体实现 - 核心智能体类

This module implements the core agent classes for the multi-agent system.
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.schema import AgentAction, AgentFinish

from .core_system import (
    AgentType, Message, ToolCall, HumanFeedback, FeedbackType,
    memory_manager, tool_registry, message_bus, ragas_validator,
    MultiAgentState, llm
)

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    name: str
    agent_type: AgentType
    system_prompt: str
    description: str
    tools: List[str] = None
    max_iterations: int = 10
    memory_enabled: bool = True
    
class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, config: AgentConfig, session_id: str):
        self.config = config
        self.session_id = session_id
        self.agent_id = f"{config.agent_type.value}_{uuid.uuid4().hex[:8]}"
        self.state = "idle"
        self.current_task = None
        self.tools = []
        
        # Subscribe to message bus
        message_bus.subscribe(self.agent_id, self.handle_message)
        
        # Initialize tools
        if config.tools:
            for tool_name in config.tools:
                tool = tool_registry.get_tool(tool_name)
                if tool:
                    self.tools.append(tool)
                    
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", config.system_prompt),
            ("human", "{input}"),
            ("messages_placeholder", "{chat_history}")
        ])
        
        logger.info(f"Agent {self.agent_id} ({config.name}) initialized")
        
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        logger.info(f"Agent {self.agent_id} received message from {message.sender}")
        
        # Process message based on type
        if message.message_type == "task":
            await self.execute_task(message.content, message.metadata)
        elif message.message_type == "query":
            await self.handle_query(message.content, message.metadata)
        elif message.message_type == "feedback":
            await self.process_feedback(message.content, message.metadata)
            
    async def execute_task(self, task_description: str, metadata: Dict = None):
        """Execute a task"""
        self.state = "working"
        self.current_task = task_description
        
        try:
            # Get conversation history
            chat_history = memory_manager.get_conversation_history(self.session_id)
            
            # Prepare input
            input_data = {
                "input": task_description,
                "chat_history": chat_history
            }
            
            # Execute with tools if available
            if self.tools:
                # Create agent executor
                agent = LLMSingleActionAgent(
                    llm_chain=llm,
                    output_parser=self._create_output_parser(),
                    stop=["\\nObservation:"],
                    allowed_tools=[tool.name for tool in self.tools]
                )
                
                executor = AgentExecutor.from_agent_and_tools(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    max_iterations=self.config.max_iterations
                )
                
                result = await executor.ainvoke(input_data)
                output = result.get("output", "Task completed")
            else:
                # Simple LLM invocation
                chain = self.prompt | llm
                result = await chain.ainvoke(input_data)
                output = result.content
                
            # Store result in memory
            memory_manager.add_message(self.session_id, "assistant", output)
            
            # Send completion message
            completion_message = Message(
                id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="coordinator",
                content=f"Task completed: {task_description}",
                timestamp=datetime.now(),
                message_type="completion",
                metadata={"result": output}
            )
            
            await message_bus.publish(completion_message)
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            error_message = Message(
                id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="coordinator",
                content=f"Task failed: {task_description}",
                timestamp=datetime.now(),
                message_type="error",
                metadata={"error": str(e)}
            )
            await message_bus.publish(error_message)
            
        finally:
            self.state = "idle"
            self.current_task = None
            
    async def handle_query(self, query: str, metadata: Dict = None):
        """Handle a query"""
        try:
            # Get conversation history
            chat_history = memory_manager.get_conversation_history(self.session_id)
            
            # Prepare input
            input_data = {
                "input": query,
                "chat_history": chat_history
            }
            
            # Generate response
            chain = self.prompt | llm
            result = await chain.ainvoke(input_data)
            response = result.content
            
            # Store in memory
            memory_manager.add_message(self.session_id, "assistant", response)
            
            # Send response
            response_message = Message(
                id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver=metadata.get("reply_to", "user"),
                content=response,
                timestamp=datetime.now(),
                message_type="response"
            )
            
            await message_bus.publish(response_message)
            
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            
    async def process_feedback(self, feedback_content: str, metadata: Dict = None):
        """Process feedback"""
        try:
            feedback_data = json.loads(feedback_content)
            feedback = HumanFeedback(
                id=str(uuid.uuid4()),
                agent_id=self.agent_id,
                phase=feedback_data.get("phase", "unknown"),
                feedback_type=FeedbackType(feedback_data.get("type", "continue")),
                score=feedback_data.get("score", 5),
                comment=feedback_data.get("comment", ""),
                timestamp=datetime.now(),
                action_taken=feedback_data.get("action_taken", ""),
                improvement=feedback_data.get("improvement", "")
            )
            
            # Store feedback
            memory_manager.add_feedback(feedback)
            
            # Adjust behavior based on feedback
            await self._adjust_behavior(feedback)
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            
    async def _adjust_behavior(self, feedback: HumanFeedback):
        """Adjust agent behavior based on feedback"""
        # This is where you would implement learning from feedback
        logger.info(f"Agent {self.agent_id} adjusting behavior based on feedback")
        
    def _create_output_parser(self):
        """Create output parser for agent execution"""
        class SimpleOutputParser:
            def parse(self, text):
                # Simple parsing - in practice, you'd want more sophisticated parsing
                return AgentFinish(
                    return_values={"output": text.strip()},
                    log=text
                )
                
        return SimpleOutputParser()

class CoordinatorAgent(BaseAgent):
    """Coordinator agent that manages other agents"""
    
    def __init__(self, session_id: str):
        config = AgentConfig(
            name="Coordinator",
            agent_type=AgentType.COORDINATOR,
            system_prompt="""You are the coordinator agent responsible for:
1. Understanding user requests and breaking them down into tasks
2. Assigning tasks to appropriate specialist agents
3. Monitoring task progress and handling errors
4. Aggregating results and providing final responses
5. Managing the overall workflow and agent coordination

Always maintain context and ensure seamless communication between agents.""",
            description="Coordinates multi-agent workflows and task distribution",
            tools=["task_planner", "progress_monitor"]
        )
        super().__init__(config, session_id)
        
        self.agents = {}
        self.task_queue = asyncio.Queue()
        self.active_tasks = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register a specialist agent"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent {agent.agent_id} with coordinator")
        
    async def process_user_input(self, user_input: str) -> str:
        """Process user input and coordinate response"""
        try:
            # Store user input
            memory_manager.add_message(self.session_id, "human", user_input)
            
            # Analyze request and determine required agents
            analysis = await self._analyze_request(user_input)
            
            # Create and distribute tasks
            tasks = await self._create_tasks(user_input, analysis)
            
            # Execute tasks and collect results
            results = await self._execute_tasks(tasks)
            
            # Generate final response
            final_response = await self._generate_response(user_input, results)
            
            # Validate response
            validation = await ragas_validator.validate_answer(
                user_input, final_response
            )
            
            # Store validation results
            memory_manager.working_memory[f"validation_{self.session_id}"] = validation
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
            
    async def _analyze_request(self, user_input: str) -> Dict:
        """Analyze user request to determine required actions"""
        analysis_prompt = f"""
        Analyze the following user request and determine:
        1. What type of request is this? (research, analysis, execution, etc.)
        2. Which specialist agents are needed?
        3. What tasks should be performed?
        4. What is the expected output format?
        
        User request: {user_input}
        
        Return your analysis as JSON.
        """
        
        try:
            response = await llm.ainvoke(analysis_prompt)
            # Parse response (simplified)
            return {
                "request_type": "general",
                "required_agents": ["researcher", "analyst"],
                "tasks": ["research", "analyze"],
                "output_format": "text"
            }
        except Exception as e:
            logger.error(f"Error analyzing request: {e}")
            return {
                "request_type": "general",
                "required_agents": ["researcher"],
                "tasks": ["research"],
                "output_format": "text"
            }
            
    async def _create_tasks(self, user_input: str, analysis: Dict) -> List[Dict]:
        """Create tasks based on analysis"""
        tasks = []
        
        for i, task_type in enumerate(analysis.get("tasks", [])):
            task = {
                "id": f"task_{i}",
                "type": task_type,
                "description": f"Perform {task_type} for: {user_input}",
                "assigned_agent": None,  # Will be assigned based on availability
                "priority": i,
                "status": "pending"
            }
            tasks.append(task)
            
        return tasks
        
    async def _execute_tasks(self, tasks: List[Dict]) -> Dict:
        """Execute tasks and collect results"""
        results = {}
        
        for task in tasks:
            try:
                # Find appropriate agent
                agent = await self._find_available_agent(task["type"])
                
                if agent:
                    task["assigned_agent"] = agent.agent_id
                    task["status"] = "in_progress"
                    
                    # Send task to agent
                    task_message = Message(
                        id=str(uuid.uuid4()),
                        sender=self.agent_id,
                        receiver=agent.agent_id,
                        content=task["description"],
                        timestamp=datetime.now(),
                        message_type="task",
                        metadata={"task_id": task["id"]}
                    )
                    
                    await message_bus.publish(task_message)
                    
                    # Wait for completion (simplified - in practice, you'd want proper async handling)
                    await asyncio.sleep(1)  # Placeholder
                    
                    task["status"] = "completed"
                    results[task["id"]] = "Task completed successfully"
                else:
                    task["status"] = "failed"
                    results[task["id"]] = "No available agent for task"
                    
            except Exception as e:
                logger.error(f"Error executing task {task['id']}: {e}")
                task["status"] = "failed"
                results[task["id"]] = f"Error: {str(e)}"
                
        return results
        
    async def _find_available_agent(self, task_type: str) -> Optional[BaseAgent]:
        """Find an available agent for the task type"""
        # Simple implementation - in practice, you'd want more sophisticated scheduling
        for agent_id, agent in self.agents.items():
            if agent.state == "idle":
                return agent
        return None
        
    async def _generate_response(self, user_input: str, results: Dict) -> str:
        """Generate final response based on task results"""
        response_prompt = f"""
        Based on the user's request and the task results, generate a comprehensive response:
        
        User request: {user_input}
        Task results: {json.dumps(results, indent=2)}
        
        Please provide a clear, helpful response that addresses the user's request.
        """
        
        try:
            response = await llm.ainvoke(response_prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating the response."

class ResearcherAgent(BaseAgent):
    """Research agent for information gathering and analysis"""
    
    def __init__(self, session_id: str):
        config = AgentConfig(
            name="Researcher",
            agent_type=AgentType.RESEARCHER,
            system_prompt="""You are a research agent specializing in:
1. Information gathering from various sources
2. Data analysis and synthesis
3. Market research and trend analysis
4. Competitive analysis
5. Fact-checking and verification

Provide thorough, well-researched information with proper citations and sources.""",
            description="Researches and analyzes information",
            tools=["web_search", "data_analyzer", "fact_checker"]
        )
        super().__init__(config, session_id)

class AnalystAgent(BaseAgent):
    """Analyst agent for data interpretation and insight generation"""
    
    def __init__(self, session_id: str):
        config = AgentConfig(
            name="Analyst",
            agent_type=AgentType.ANALYST,
            system_prompt="""You are an analyst agent specializing in:
1. Data interpretation and pattern recognition
2. Statistical analysis and modeling
3. Trend identification and forecasting
4. Risk assessment and mitigation
5. Strategic insight generation

Provide deep insights and actionable recommendations based on thorough analysis.""",
            description="Analyzes data and generates insights",
            tools=["data_analyzer", "statistical_tools", "visualizer"]
        )
        super().__init__(config, session_id)

class ExecutorAgent(BaseAgent):
    """Executor agent for task implementation and action execution"""
    
    def __init__(self, session_id: str):
        config = AgentConfig(
            name="Executor",
            agent_type=AgentType.EXECUTOR,
            system_prompt="""You are an executor agent specializing in:
1. Implementing planned actions and strategies
2. Coordinating multi-step workflows
3. Managing resources and timelines
4. Executing transactions and operations
5. Monitoring progress and adjusting plans

Ensure efficient and accurate execution of all assigned tasks.""",
            description="Executes tasks and manages workflows",
            tools=["task_manager", "resource_planner", "workflow_executor"]
        )
        super().__init__(config, session_id)

class ValidatorAgent(BaseAgent):
    """Validator agent for quality assurance and validation"""
    
    def __init__(self, session_id: str):
        config = AgentConfig(
            name="Validator",
            agent_type=AgentType.VALIDATOR,
            system_prompt="""You are a validator agent specializing in:
1. Quality assurance and validation
2. Accuracy checking and verification
3. Compliance and standards checking
4. Performance evaluation
5. Risk assessment and mitigation

Ensure all outputs meet quality standards and requirements.""",
            description="Validates outputs and ensures quality",
            tools=["quality_checker", "compliance_validator", "risk_assessor"]
        )
        super().__init__(config, session_id)