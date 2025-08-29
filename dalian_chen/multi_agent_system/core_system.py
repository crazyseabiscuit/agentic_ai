#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive Multi-Agent System with Memory, Tools, and Human Feedback
集成记忆管理、工具调用和人类反馈的综合性多智能体系统

Features:
- Short-term and long-term memory management
- Dynamic tool integration
- Human feedback mechanism with RAGAS validation
- Multi-agent coordination
- Real-time communication and collaboration
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, TypedDict, Literal
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
from pathlib import Path

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Tongyi
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.schema import AgentAction, AgentFinish

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_agent_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DASHSCOPE_API_KEY = 'sk-882e296067b744289acf27e6e20f3ec0'
DATABASE_PATH = 'multi_agent_memory.db'

# Initialize LLM
llm = Tongyi(model_name="Qwen-Turbo-2025-04-28", dashscope_api_key=DASHSCOPE_API_KEY)

class AgentType(Enum):
    """Agent types in the system"""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    EXECUTOR = "executor"
    VALIDATOR = "validator"

class FeedbackType(Enum):
    """Types of human feedback"""
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    CONTINUE = "continue"

class MemoryType(Enum):
    """Types of memory storage"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"

@dataclass
class Message:
    """Message structure for agent communication"""
    id: str
    sender: str
    receiver: str
    content: str
    timestamp: datetime
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ToolCall:
    """Tool call representation"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class HumanFeedback:
    """Human feedback structure"""
    id: str
    agent_id: str
    phase: str
    feedback_type: FeedbackType
    score: int  # 1-10
    comment: str
    timestamp: datetime
    action_taken: str
    improvement: str

class MemoryManager:
    """Comprehensive memory management system"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.short_term_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.long_term_memory = ConversationSummaryMemory(
            llm=llm,
            memory_key="chat_history",
            return_messages=True
        )
        self.working_memory = {}
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for persistent memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                comment TEXT,
                action_taken TEXT,
                improvement TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                parameters TEXT NOT NULL,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to memory"""
        # Add to short-term memory
        if role == "human":
            self.short_term_memory.chat_memory.add_user_message(content)
        else:
            self.short_term_memory.chat_memory.add_ai_message(content)
            
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
        conn.close()
        
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content, timestamp FROM conversations "
            "WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]}
            for row in reversed(results)
        ]
        
    def add_feedback(self, feedback: HumanFeedback):
        """Store human feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback_history "
            "(agent_id, phase, feedback_type, score, comment, action_taken, improvement) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                feedback.agent_id,
                feedback.phase,
                feedback.feedback_type.value,
                feedback.score,
                feedback.comment,
                feedback.action_taken,
                feedback.improvement
            )
        )
        conn.commit()
        conn.close()
        
    def get_feedback_history(self, agent_id: str = None) -> List[HumanFeedback]:
        """Get feedback history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if agent_id:
            cursor.execute(
                "SELECT * FROM feedback_history WHERE agent_id = ? ORDER BY timestamp DESC",
                (agent_id,)
            )
        else:
            cursor.execute("SELECT * FROM feedback_history ORDER BY timestamp DESC")
            
        results = cursor.fetchall()
        conn.close()
        
        return [
            HumanFeedback(
                id=str(row[0]),
                agent_id=row[1],
                phase=row[2],
                feedback_type=FeedbackType(row[3]),
                score=row[4],
                comment=row[5],
                timestamp=datetime.fromisoformat(row[9]),
                action_taken=row[7],
                improvement=row[8]
            )
            for row in results
        ]
        
    def store_tool_call(self, agent_id: str, tool_call: ToolCall):
        """Store tool call in memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tool_calls (agent_id, tool_name, parameters, result) "
            "VALUES (?, ?, ?, ?)",
            (
                agent_id,
                tool_call.tool_name,
                json.dumps(tool_call.parameters),
                json.dumps(tool_call.result) if tool_call.result else None
            )
        )
        conn.commit()
        conn.close()

class ToolRegistry:
    """Dynamic tool registration and management system"""
    
    def __init__(self):
        self.tools = {}
        self.tool_categories = {
            "search": [],
            "analysis": [],
            "communication": [],
            "calculation": [],
            "data_processing": []
        }
        
    def register_tool(self, name: str, tool_func: callable, description: str, 
                     category: str = "general", parameters_schema: Dict = None):
        """Register a new tool"""
        tool = Tool(
            name=name,
            func=tool_func,
            description=description,
            args_schema=parameters_schema
        )
        
        self.tools[name] = {
            "tool": tool,
            "category": category,
            "description": description,
            "usage_count": 0
        }
        
        if category not in self.tool_categories:
            self.tool_categories[category] = []
        self.tool_categories[category].append(name)
        
        logger.info(f"Tool '{name}' registered in category '{category}'")
        
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        if name in self.tools:
            self.tools[name]["usage_count"] += 1
            return self.tools[name]["tool"]
        return None
        
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a category"""
        return [
            self.tools[name]["tool"] 
            for name in self.tool_categories.get(category, [])
            if name in self.tools
        ]
        
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return [tool_data["tool"] for tool_data in self.tools.values()]
        
    def list_tools(self) -> Dict[str, List[str]]:
        """List all tools by category"""
        return self.tool_categories

class MessageBus:
    """Communication system for agents"""
    
    def __init__(self):
        self.subscribers = {}
        self.message_queue = asyncio.Queue()
        self.message_history = []
        
    def subscribe(self, agent_id: str, callback: callable):
        """Subscribe an agent to receive messages"""
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)
        
    async def publish(self, message: Message):
        """Publish a message to the bus"""
        self.message_history.append(message)
        await self.message_queue.put(message)
        
        # Deliver to subscribers
        if message.receiver in self.subscribers:
            for callback in self.subscribers[message.receiver]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Error delivering message to {message.receiver}: {e}")
                    
    async def get_message(self) -> Message:
        """Get next message from queue"""
        return await self.message_queue.get()

class RAGASValidator:
    """RAGAS-based validation system for agent outputs"""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def validate_answer(self, question: str, answer: str, 
                            context: str = None) -> Dict[str, float]:
        """Validate answer using RAGAS metrics"""
        
        validation_prompt = f"""
        Please evaluate the following answer based on these criteria:
        
        Question: {question}
        Answer: {answer}
        Context: {context or 'No additional context provided'}
        
        Rate the following aspects on a scale of 0.0 to 1.0:
        1. Faithfulness: How well does the answer adhere to the provided context?
        2. Answer Relevance: How relevant is the answer to the question?
        3. Context Relevance: How relevant is the context to the question?
        4. Answer Correctness: How factually correct is the answer?
        
        Return your evaluation as JSON with these metrics.
        """
        
        try:
            response = await self.llm.ainvoke(validation_prompt)
            # Parse the response to extract metrics
            # This is a simplified version - in practice, you'd want more robust parsing
            return {
                "faithfulness": 0.8,  # Placeholder
                "answer_relevance": 0.9,
                "context_relevance": 0.7,
                "answer_correctness": 0.85,
                "overall_score": 0.81
            }
        except Exception as e:
            logger.error(f"RAGAS validation error: {e}")
            return {
                "faithfulness": 0.5,
                "answer_relevance": 0.5,
                "context_relevance": 0.5,
                "answer_correctness": 0.5,
                "overall_score": 0.5
            }

# Global instances
memory_manager = MemoryManager()
tool_registry = ToolRegistry()
message_bus = MessageBus()
ragas_validator = RAGASValidator(llm)

# System state definition
class MultiAgentState(TypedDict):
    """State for the multi-agent system"""
    session_id: str
    user_input: str
    current_agent: str
    messages: List[Dict]
    working_data: Dict[str, Any]
    tool_results: Dict[str, Any]
    feedback_history: List[Dict]
    validation_results: Dict[str, Any]
    final_output: Optional[str]
    error: Optional[str]