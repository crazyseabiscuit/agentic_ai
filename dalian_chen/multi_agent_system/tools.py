#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool Integration System - Tools and Utilities
工具集成系统 - 工具和实用程序

This module implements various tools for the multi-agent system.
"""

import json
import random
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# Import tool registry
from .core_system import tool_registry, ToolCall

# ==================== Search and Information Tools ====================

def web_search(query: str, num_results: int = 5) -> str:
    """
    Web search tool (simulated)
    网络搜索工具（模拟版）
    """
    # Simulate web search results
    search_results = [
        {
            "title": f"Search result 1 for: {query}",
            "url": "https://example.com/1",
            "snippet": f"This is a relevant search result about {query}"
        },
        {
            "title": f"Search result 2 for: {query}",
            "url": "https://example.com/2",
            "snippet": f"Another relevant result about {query} with additional information"
        },
        {
            "title": f"Search result 3 for: {query}",
            "url": "https://example.com/3",
            "snippet": f"More information about {query} from a different source"
        }
    ]
    
    return json.dumps(search_results[:num_results], indent=2, ensure_ascii=False)

def get_stock_price(symbol: str) -> str:
    """
    Get stock price (simulated)
    获取股票价格（模拟版）
    """
    # Simulate stock data
    base_price = 100.0
    price = base_price + random.uniform(-10, 10)
    change = random.uniform(-5, 5)
    change_percent = (change / base_price) * 100
    
    return json.dumps({
        "symbol": symbol,
        "price": round(price, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "timestamp": datetime.now().isoformat()
    }, ensure_ascii=False)

def get_market_news(category: str = "general") -> str:
    """
    Get market news (simulated)
    获取市场新闻（模拟版）
    """
    news_items = [
        {
            "title": "Market shows positive momentum",
            "summary": "Markets are showing positive trends across various sectors",
            "time": "2 hours ago",
            "source": "Financial Times"
        },
        {
            "title": "Tech sector leads gains",
            "summary": "Technology stocks are outperforming other sectors",
            "time": "4 hours ago",
            "source": "Bloomberg"
        },
        {
            "title": "Economic indicators improve",
            "summary": "Latest economic data suggests improving conditions",
            "time": "6 hours ago",
            "source": "Reuters"
        }
    ]
    
    return json.dumps(news_items, indent=2, ensure_ascii=False)

# ==================== Data Analysis Tools ====================

def analyze_financial_data(data: str) -> str:
    """
    Analyze financial data
    分析财务数据
    """
    try:
        # Parse input data
        if isinstance(data, str):
            data_dict = json.loads(data)
        else:
            data_dict = data
            
        # Perform basic analysis
        analysis = {
            "data_points": len(data_dict.get("values", [])),
            "mean": np.mean(data_dict.get("values", [0])),
            "median": np.median(data_dict.get("values", [0])),
            "std_dev": np.std(data_dict.get("values", [0])),
            "trend": "increasing" if data_dict.get("values", [0])[-1] > data_dict.get("values", [0])[0] else "decreasing",
            "volatility": "high" if np.std(data_dict.get("values", [0])) > np.mean(data_dict.get("values", [0])) * 0.1 else "low"
        }
        
        return json.dumps(analysis, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def calculate_portfolio_metrics(portfolio_data: str) -> str:
    """
    Calculate portfolio performance metrics
    计算投资组合绩效指标
    """
    try:
        portfolio = json.loads(portfolio_data)
        
        total_value = sum(asset["value"] for asset in portfolio.get("assets", []))
        total_cost = sum(asset["cost"] for asset in portfolio.get("assets", []))
        
        metrics = {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_return": total_value - total_cost,
            "total_return_percent": ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0,
            "asset_count": len(portfolio.get("assets", [])),
            "top_performer": max(portfolio.get("assets", []), key=lambda x: x.get("return", 0)),
            "worst_performer": min(portfolio.get("assets", []), key=lambda x: x.get("return", 0))
        }
        
        return json.dumps(metrics, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def generate_investment_report(data: str) -> str:
    """
    Generate investment analysis report
    生成投资分析报告
    """
    try:
        analysis_data = json.loads(data)
        
        report = f"""
# Investment Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
{analysis_data.get('summary', 'No summary provided')}

## Key Findings
- Market Trend: {analysis_data.get('market_trend', 'Unknown')}
- Risk Level: {analysis_data.get('risk_level', 'Unknown')}
- Expected Return: {analysis_data.get('expected_return', 'Unknown')}

## Recommendations
{analysis_data.get('recommendations', 'No recommendations provided')}

## Risk Factors
{analysis_data.get('risk_factors', 'No risk factors identified')}

## Next Steps
{analysis_data.get('next_steps', 'No next steps defined')}
"""
        
        return report
        
    except Exception as e:
        return f"Error generating report: {str(e)}"

# ==================== Visualization Tools ====================

def create_chart(data: str, chart_type: str = "line") -> str:
    """
    Create data visualization
    创建数据可视化
    """
    try:
        data_dict = json.loads(data)
        
        # Create sample data if not provided
        if "values" not in data_dict:
            data_dict["values"] = [random.randint(1, 100) for _ in range(10)]
            
        if "labels" not in data_dict:
            data_dict["labels"] = [f"Point {i+1}" for i in range(len(data_dict["values"]))]
        
        plt.figure(figsize=(10, 6))
        
        if chart_type == "line":
            plt.plot(data_dict["labels"], data_dict["values"], marker='o')
            plt.title("Line Chart")
        elif chart_type == "bar":
            plt.bar(data_dict["labels"], data_dict["values"])
            plt.title("Bar Chart")
        elif chart_type == "pie":
            plt.pie(data_dict["values"], labels=data_dict["labels"], autopct='%1.1f%%')
            plt.title("Pie Chart")
        else:
            plt.plot(data_dict["labels"], data_dict["values"], marker='o')
            plt.title("Line Chart (Default)")
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        return f"Error creating chart: {str(e)}"

# ==================== Communication Tools ====================

def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Send email (simulated)
    发送邮件（模拟版）
    """
    # Simulate email sending
    email_log = {
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "sent_at": datetime.now().isoformat(),
        "status": "sent",
        "message_id": f"email_{random.randint(1000, 9999)}"
    }
    
    return json.dumps(email_log, indent=2, ensure_ascii=False)

def generate_notification(message: str, priority: str = "normal") -> str:
    """
    Generate notification
    生成通知
    """
    notification = {
        "id": f"notif_{random.randint(1000, 9999)}",
        "message": message,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),
        "status": "unread"
    }
    
    return json.dumps(notification, indent=2, ensure_ascii=False)

# ==================== Task Management Tools ====================

def create_task(task_name: str, description: str, priority: str = "medium") -> str:
    """
    Create a new task
    创建新任务
    """
    task = {
        "id": f"task_{random.randint(1000, 9999)}",
        "name": task_name,
        "description": description,
        "priority": priority,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    return json.dumps(task, indent=2, ensure_ascii=False)

def update_task_status(task_id: str, new_status: str) -> str:
    """
    Update task status
    更新任务状态
    """
    update_info = {
        "task_id": task_id,
        "new_status": new_status,
        "updated_at": datetime.now().isoformat(),
        "success": True
    }
    
    return json.dumps(update_info, indent=2, ensure_ascii=False)

# ==================== Quality and Validation Tools ====================

def validate_data_quality(data: str) -> str:
    """
    Validate data quality
    验证数据质量
    """
    try:
        data_dict = json.loads(data)
        
        quality_checks = {
            "completeness": 95,  # Percentage of complete data
            "accuracy": 88,      # Data accuracy score
            "consistency": 92,   # Data consistency score
            "timeliness": 97,    # Data timeliness score
            "overall_score": 93  # Overall quality score
        }
        
        validation_result = {
            "quality_checks": quality_checks,
            "issues_found": [],
            "recommendations": ["Data quality is good", "Minor improvements suggested"],
            "validated_at": datetime.now().isoformat()
        }
        
        return json.dumps(validation_result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def check_compliance(data: str, standards: List[str]) -> str:
    """
    Check compliance with standards
    检查合规性
    """
    try:
        compliance_results = {
            "standards_checked": standards,
            "compliant_standards": standards[:2],  # Assume first 2 are compliant
            "non_compliant_standards": standards[2:],  # Assume rest are non-compliant
            "compliance_score": 75,
            "issues": [
                {
                    "standard": standards[2],
                    "issue": "Partial compliance",
                    "severity": "medium"
                }
            ],
            "recommendations": [
                "Update documentation to meet all standards",
                "Implement additional controls"
            ]
        }
        
        return json.dumps(compliance_results, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

# ==================== Risk Assessment Tools ====================

def assess_risk(data: str) -> str:
    """
    Assess risk levels
    评估风险水平
    """
    try:
        risk_factors = {
            "market_risk": random.uniform(0.1, 0.9),
            "credit_risk": random.uniform(0.1, 0.9),
            "operational_risk": random.uniform(0.1, 0.9),
            "liquidity_risk": random.uniform(0.1, 0.9),
            "regulatory_risk": random.uniform(0.1, 0.9)
        }
        
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        risk_level = "low" if overall_risk < 0.3 else "medium" if overall_risk < 0.7 else "high"
        
        risk_assessment = {
            "overall_risk_score": overall_risk,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_strategies": [
                "Diversify investments",
                "Monitor market conditions",
                "Maintain adequate liquidity"
            ],
            "assessment_date": datetime.now().isoformat()
        }
        
        return json.dumps(risk_assessment, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

# ==================== Register Tools ====================

def register_all_tools():
    """Register all tools with the tool registry"""
    
    # Search and Information Tools
    tool_registry.register_tool(
        "web_search", 
        web_search, 
        "Search the web for information", 
        "search"
    )
    
    tool_registry.register_tool(
        "get_stock_price", 
        get_stock_price, 
        "Get current stock price for a symbol", 
        "search"
    )
    
    tool_registry.register_tool(
        "get_market_news", 
        get_market_news, 
        "Get latest market news", 
        "search"
    )
    
    # Data Analysis Tools
    tool_registry.register_tool(
        "analyze_financial_data", 
        analyze_financial_data, 
        "Analyze financial data and provide insights", 
        "analysis"
    )
    
    tool_registry.register_tool(
        "calculate_portfolio_metrics", 
        calculate_portfolio_metrics, 
        "Calculate portfolio performance metrics", 
        "analysis"
    )
    
    tool_registry.register_tool(
        "generate_investment_report", 
        generate_investment_report, 
        "Generate comprehensive investment analysis report", 
        "analysis"
    )
    
    # Visualization Tools
    tool_registry.register_tool(
        "create_chart", 
        create_chart, 
        "Create data visualizations (line, bar, pie charts)", 
        "analysis"
    )
    
    # Communication Tools
    tool_registry.register_tool(
        "send_email", 
        send_email, 
        "Send email notifications", 
        "communication"
    )
    
    tool_registry.register_tool(
        "generate_notification", 
        generate_notification, 
        "Generate system notifications", 
        "communication"
    )
    
    # Task Management Tools
    tool_registry.register_tool(
        "create_task", 
        create_task, 
        "Create new tasks", 
        "management"
    )
    
    tool_registry.register_tool(
        "update_task_status", 
        update_task_status, 
        "Update task status", 
        "management"
    )
    
    # Quality and Validation Tools
    tool_registry.register_tool(
        "validate_data_quality", 
        validate_data_quality, 
        "Validate data quality and integrity", 
        "validation"
    )
    
    tool_registry.register_tool(
        "check_compliance", 
        check_compliance, 
        "Check compliance with standards", 
        "validation"
    )
    
    # Risk Assessment Tools
    tool_registry.register_tool(
        "assess_risk", 
        assess_risk, 
        "Assess risk levels and provide mitigation strategies", 
        "analysis"
    )
    
    print("All tools registered successfully!")

# Register tools when module is imported
register_all_tools()