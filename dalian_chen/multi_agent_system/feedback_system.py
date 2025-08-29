#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Human Feedback Mechanism - Interactive Feedback System
人类反馈机制 - 交互式反馈系统

This module implements the human feedback mechanism for the multi-agent system.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from queue import Queue

from .core_system import (
    HumanFeedback, FeedbackType, memory_manager, message_bus
)

class FeedbackInterface:
    """Interactive feedback interface"""
    
    def __init__(self):
        self.feedback_queue = Queue()
        self.active_sessions = {}
        self.feedback_callbacks = {}
        
    def request_feedback(self, session_id: str, agent_id: str, phase: str, 
                        content: str, context: Dict = None) -> str:
        """
        Request human feedback for a specific agent action
        请求对特定智能体操作的人类反馈
        """
        feedback_request = {
            "session_id": session_id,
            "agent_id": agent_id,
            "phase": phase,
            "content": content,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Add to queue
        self.feedback_queue.put(feedback_request)
        
        # Show feedback dialog
        self._show_feedback_dialog(feedback_request)
        
        return feedback_request
        
    def _show_feedback_dialog(self, feedback_request: Dict):
        """Show feedback dialog (simplified console version)"""
        print(f"\n{'='*60}")
        print(f"FEEDBACK REQUEST - {feedback_request['phase']}")
        print(f"{'='*60}")
        print(f"Agent: {feedback_request['agent_id']}")
        print(f"Session: {feedback_request['session_id']}")
        print(f"\nContent:")
        print(feedback_request['content'])
        print(f"\n{'='*60}")
        
        # Get feedback type
        print("\nFeedback Types:")
        print("1. Approve (approve)")
        print("2. Reject (reject)")
        print("3. Request Modification (modify)")
        print("4. Continue (continue)")
        
        while True:
            try:
                choice = input("\nSelect feedback type (1-4): ")
                feedback_map = {
                    "1": FeedbackType.APPROVE,
                    "2": FeedbackType.REJECT,
                    "3": FeedbackType.MODIFY,
                    "4": FeedbackType.CONTINUE
                }
                
                if choice in feedback_map:
                    feedback_type = feedback_map[choice]
                    break
                else:
                    print("Invalid choice. Please select 1-4.")
            except KeyboardInterrupt:
                print("\nFeedback cancelled.")
                return
                
        # Get score
        while True:
            try:
                score = int(input("Rate performance (1-10): "))
                if 1 <= score <= 10:
                    break
                else:
                    print("Score must be between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nFeedback cancelled.")
                return
                
        # Get comment
        comment = input("Additional comments (optional): ").strip()
        
        # Determine action taken
        action_taken = ""
        if feedback_type == FeedbackType.APPROVE:
            action_taken = "继续下一阶段"
        elif feedback_type == FeedbackType.REJECT:
            action_taken = "重新执行当前阶段"
        elif feedback_type == FeedbackType.MODIFY:
            action_taken = "根据反馈修改后继续"
        elif feedback_type == FeedbackType.CONTINUE:
            action_taken = "继续执行"
            
        # Create feedback object
        feedback = HumanFeedback(
            id=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_id=feedback_request['agent_id'],
            phase=feedback_request['phase'],
            feedback_type=feedback_type,
            score=score,
            comment=comment,
            timestamp=datetime.now(),
            action_taken=action_taken,
            improvement=comment
        )
        
        # Store feedback
        memory_manager.add_feedback(feedback)
        
        # Notify system
        self._notify_feedback_received(feedback)
        
        print(f"\nFeedback recorded: {feedback_type.value} (Score: {score}/10)")
        
    def _notify_feedback_received(self, feedback: HumanFeedback):
        """Notify system that feedback was received"""
        # This would typically send a message to the coordinator
        # For now, just log it
        print(f"Feedback received from {feedback.agent_id} at {feedback.phase}")
        
    def get_feedback_history(self, agent_id: str = None) -> List[HumanFeedback]:
        """Get feedback history"""
        return memory_manager.get_feedback_history(agent_id)
        
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze feedback patterns for insights"""
        feedback_history = self.get_feedback_history()
        
        if not feedback_history:
            return {"message": "No feedback history available"}
            
        analysis = {
            "total_feedback_count": len(feedback_history),
            "average_score": sum(f.score for f in feedback_history) / len(feedback_history),
            "feedback_type_distribution": {},
            "phase_performance": {},
            "agent_performance": {},
            "improvement_areas": []
        }
        
        # Analyze feedback types
        for feedback in feedback_history:
            ftype = feedback.feedback_type.value
            analysis["feedback_type_distribution"][ftype] = analysis["feedback_type_distribution"].get(ftype, 0) + 1
            
        # Analyze phase performance
        for feedback in feedback_history:
            phase = feedback.phase
            if phase not in analysis["phase_performance"]:
                analysis["phase_performance"][phase] = []
            analysis["phase_performance"][phase].append(feedback.score)
            
        # Calculate average scores per phase
        for phase, scores in analysis["phase_performance"].items():
            analysis["phase_performance"][phase] = sum(scores) / len(scores)
            
        # Analyze agent performance
        for feedback in feedback_history:
            agent = feedback.agent_id
            if agent not in analysis["agent_performance"]:
                analysis["agent_performance"][agent] = []
            analysis["agent_performance"][agent].append(feedback.score)
            
        # Calculate average scores per agent
        for agent, scores in analysis["agent_performance"].items():
            analysis["agent_performance"][agent] = sum(scores) / len(scores)
            
        # Identify improvement areas (phases/agents with low scores)
        for phase, score in analysis["phase_performance"].items():
            if score < 7.0:
                analysis["improvement_areas"].append(f"Phase: {phase} (Score: {score:.1f})")
                
        for agent, score in analysis["agent_performance"].items():
            if score < 7.0:
                analysis["improvement_areas"].append(f"Agent: {agent} (Score: {score:.1f})")
                
        return analysis

class FeedbackLearningSystem:
    """Learning system based on human feedback"""
    
    def __init__(self):
        self.feedback_patterns = {}
        self.adaptation_rules = {}
        
    def learn_from_feedback(self, feedback: HumanFeedback):
        """Learn from feedback and adapt behavior"""
        # Store feedback pattern
        pattern_key = f"{feedback.agent_id}_{feedback.phase}"
        
        if pattern_key not in self.feedback_patterns:
            self.feedback_patterns[pattern_key] = []
            
        self.feedback_patterns[pattern_key].append({
            "feedback_type": feedback.feedback_type,
            "score": feedback.score,
            "comment": feedback.comment,
            "timestamp": feedback.timestamp
        })
        
        # Analyze patterns and suggest adaptations
        self._analyze_and_adapt(pattern_key)
        
    def _analyze_and_adapt(self, pattern_key: str):
        """Analyze feedback patterns and suggest adaptations"""
        if pattern_key not in self.feedback_patterns:
            return
            
        patterns = self.feedback_patterns[pattern_key]
        recent_patterns = patterns[-5:]  # Last 5 feedback instances
        
        if len(recent_patterns) < 3:
            return  # Not enough data
            
        # Calculate average recent score
        avg_score = sum(p["score"] for p in recent_patterns) / len(recent_patterns)
        
        # Generate adaptation suggestions
        adaptations = []
        
        if avg_score < 5.0:
            adaptations.append("Major improvements needed")
        elif avg_score < 7.0:
            adaptations.append("Minor improvements suggested")
        elif avg_score < 8.5:
            adaptations.append("Maintain current performance")
        else:
            adaptations.append("Excellent performance - consider sharing best practices")
            
        # Check for consistent feedback types
        feedback_types = [p["feedback_type"] for p in recent_patterns]
        if all(ft == FeedbackType.REJECT for ft in feedback_types):
            adaptations.append("Consistent rejection - consider major approach changes")
        elif all(ft == FeedbackType.MODIFY for ft in feedback_types):
            adaptations.append("Frequent modifications needed - improve planning phase")
            
        # Store adaptation rules
        self.adaptation_rules[pattern_key] = {
            "average_score": avg_score,
            "adaptations": adaptations,
            "last_updated": datetime.now()
        }
        
    def get_adaptation_suggestions(self, agent_id: str, phase: str) -> List[str]:
        """Get adaptation suggestions for an agent in a specific phase"""
        pattern_key = f"{agent_id}_{phase}"
        
        if pattern_key in self.adaptation_rules:
            return self.adaptation_rules[pattern_key]["adaptations"]
        else:
            return ["No specific adaptations suggested (insufficient data)"]
            
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report based on feedback"""
        report = f"""
# Performance Report Based on Human Feedback
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total feedback patterns analyzed: {len(self.feedback_patterns)}
- Adaptation rules generated: {len(self.adaptation_rules)}

## Performance Insights
"""
        
        for pattern_key, rules in self.adaptation_rules.items():
            agent_id, phase = pattern_key.split('_', 1)
            report += f"""
### {agent_id} - {phase}
- Average Score: {rules['average_score']:.1f}/10
- Adaptations: {', '.join(rules['adaptations'])}
"""
            
        return report

# Global instances
feedback_interface = FeedbackInterface()
feedback_learning_system = FeedbackLearningSystem()

# Integration functions for the multi-agent system

def integrate_feedback_with_agents():
    """Integrate feedback system with agent workflows"""
    
    # This would be called during agent initialization
    # to set up feedback hooks and callbacks
    
    def feedback_callback(feedback: HumanFeedback):
        """Callback for when feedback is received"""
        # Add to learning system
        feedback_learning_system.learn_from_feedback(feedback)
        
        # Log the feedback
        print(f"Feedback processed: {feedback.agent_id} - {feedback.phase} - {feedback.feedback_type.value}")
        
    # Register callback
    feedback_interface.feedback_callbacks["default"] = feedback_callback
    
    print("Feedback system integrated with agents")

def get_feedback_for_session(session_id: str) -> List[HumanFeedback]:
    """Get all feedback for a specific session"""
    all_feedback = memory_manager.get_feedback_history()
    return [f for f in all_feedback if f.agent_id.startswith(session_id)]

def should_request_feedback(agent_id: str, phase: str) -> bool:
    """Determine if feedback should be requested"""
    # Simple logic - could be made more sophisticated
    # For now, request feedback for key phases
    key_phases = ["planning", "analysis", "decision", "report"]
    return phase in key_phases

def request_feedback_if_needed(agent_id: str, phase: str, content: str, 
                             session_id: str, context: Dict = None) -> Optional[HumanFeedback]:
    """Request feedback if needed for the current phase"""
    if should_request_feedback(agent_id, phase):
        feedback_request = feedback_interface.request_feedback(
            session_id, agent_id, phase, content, context
        )
        return feedback_request
    return None

# Auto-feedback collection for automated scenarios

class AutoFeedbackCollector:
    """Automated feedback collection for testing and evaluation"""
    
    def __init__(self):
        self.feedback_scenarios = {
            "high_performance": {
                "score_range": (8, 10),
                "feedback_types": [FeedbackType.APPROVE, FeedbackType.CONTINUE],
                "comments": ["Excellent work", "Good analysis", "Well done"]
            },
            "medium_performance": {
                "score_range": (6, 7),
                "feedback_types": [FeedbackType.MODIFY, FeedbackType.CONTINUE],
                "comments": ["Good but could be better", "Needs minor improvements"]
            },
            "low_performance": {
                "score_range": (1, 5),
                "feedback_types": [FeedbackType.REJECT, FeedbackType.MODIFY],
                "comments": ["Needs significant improvement", "Approach needs revision"]
            }
        }
        
    def generate_auto_feedback(self, agent_id: str, phase: str, 
                             performance_level: str = "medium_performance") -> HumanFeedback:
        """Generate automated feedback for testing"""
        import random
        
        scenario = self.feedback_scenarios.get(performance_level, self.feedback_scenarios["medium_performance"])
        
        feedback = HumanFeedback(
            id=f"auto_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            agent_id=agent_id,
            phase=phase,
            feedback_type=random.choice(scenario["feedback_types"]),
            score=random.randint(*scenario["score_range"]),
            comment=random.choice(scenario["comments"]),
            timestamp=datetime.now(),
            action_taken="Auto-generated feedback",
            improvement="Auto-generated improvement suggestion"
        )
        
        # Store feedback
        memory_manager.add_feedback(feedback)
        
        return feedback
        
    def run_feedback_simulation(self, agent_id: str, phases: List[str], 
                              performance_levels: List[str] = None) -> List[HumanFeedback]:
        """Run a feedback simulation"""
        if performance_levels is None:
            performance_levels = ["high_performance", "medium_performance", "low_performance"]
            
        feedback_list = []
        
        for i, phase in enumerate(phases):
            level = performance_levels[i % len(performance_levels)]
            feedback = self.generate_auto_feedback(agent_id, phase, level)
            feedback_list.append(feedback)
            
        return feedback_list

# Initialize the feedback system
integrate_feedback_with_agents()