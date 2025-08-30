# Advanced Long Short-Term Memory System for AI Agents

## 概述

这个项目实现了一个基于 LangGraph 过程记忆概念的高级长短期记忆系统，为 AI 智能体提供强大的记忆能力。系统采用双存储架构，支持多种记忆类型、智能检索、自动压缩和持久化存储。

## 核心特性

### 🧠 双存储架构
- **短期记忆**: 临时存储最近的交互和上下文
- **长期记忆**: 持久存储重要信息和学习成果
- **自动容量管理**: 智能的内存清理和整合机制

### 🏷️ 多种记忆类型
- **过程性记忆 (Procedural)**: 操作步骤和技能
- **情景记忆 (Episodic)**: 特定事件和经历
- **语义记忆 (Semantic)**: 一般知识和概念
- **工作记忆 (Working)**: 当前任务上下文

### 🔍 智能检索系统
- **相关性评分**: 基于内容、优先级、时效性和上下文的多维度评分
- **关键词搜索**: 快速的内容匹配
- **上下文感知**: 考虑用户ID、会话等上下文信息

### 📊 记忆管理
- **优先级系统**: LOW/MEDIUM/HIGH/CRITICAL 四级优先级
- **访问追踪**: 记录访问次数和最后访问时间
- **自动压缩**: 智能的总结和合并机制
- **定期整合**: 将短期记忆转换为长期记忆

## 系统架构

### 核心组件

```
LongShortTermMemory (主系统)
├── MemoryStore (存储接口)
│   ├── InMemoryStore (内存存储)
│   └── [可扩展] FileStore, DatabaseStore
├── MemorySummarizer (记忆压缩器)
├── MemoryRetriever (记忆检索器)
└── MemoryEntry (记忆条目)
```

### 数据流

1. **记忆存储**: 用户输入 → 创建MemoryEntry → 存储到对应存储器
2. **记忆检索**: 查询请求 → 相关性评分 → 返回排序结果
3. **记忆整合**: 定期检查 → 压缩短期记忆 → 转移到长期记忆

## 使用示例

### 基础使用

```python
from memory_system import LongShortTermMemory, MemoryType, MemoryPriority

# 创建记忆系统
memory = LongShortTermMemory()

# 添加记忆
memory.add_memory(
    content="用户Alice喜欢Python编程",
    memory_type=MemoryType.LONG_TERM,
    priority=MemoryPriority.HIGH,
    tags=['preference', 'programming'],
    context={'user_id': 'alice'}
)

# 检索相关记忆
relevant_memories = memory.retrieve_memories(
    "Alice Python", 
    limit=5
)
```

### 智能体集成

```python
from agent_memory_system import AgentWithMemory

# 创建带记忆的智能体
agent = AgentWithMemory()

# 处理消息
response = agent.process_message(
    "我的名字是Bob，我喜欢下棋",
    user_id="user_bob"
)

# 后续交互会自动使用记忆
response2 = agent.process_message(
    "我的名字是什么？",
    user_id="user_bob"
)  # 会记住Bob的名字
```

### LangGraph 集成

```python
from langgraph_integration import LangGraphMemoryAgent

# 创建LangGraph记忆智能体
agent = LangGraphMemoryAgent()

# 通过完整工作流处理查询
response = agent.process_query(
    "我想学习机器学习",
    user_id="user_ml"
)
```

## 技术特点

### 🚀 高性能
- 内存存储，快速访问
- 智能索引，高效检索
- 异步处理支持

### 🔧 可扩展
- 模块化设计
- 插件式存储后端
- 自定义评分算法

### 💾 持久化
- JSON格式存储
- 状态保存/恢复
- 备份和迁移支持

### 🧩 灵活配置
- 可调容量限制
- 自定义压缩策略
- 多种检索策略

## 文件结构

```
agent_memory_system/
├── memory_system.py          # 核心记忆系统
├── langgraph_integration.py  # LangGraph集成
├── simple_demo.py            # 简化演示版本
├── README.md                 # 项目说明
└── pyproject.toml           # UV配置
```

## 安装和运行

### 使用UV (推荐)

```bash
# 创建环境
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -e .

# 运行演示
python simple_demo.py
```

### 直接运行

```bash
# 基础演示
python memory_system.py

# 简化演示 (无外部依赖)
python simple_demo.py
```

## 应用场景

### 🤖 对话机器人
- 记住用户偏好和历史
- 维护对话上下文
- 个性化响应

### 📚 学习助手
- 跟踪学习进度
- 个性化教学内容
- 知识点关联

### 👥 客户服务
- 客户历史记录
- 问题解决模式
- 个性化服务

### 🎮 游戏AI
- 玩家行为模式
- 游戏状态记忆
- 策略学习

## 性能优化

### 内存管理
- 自动清理低优先级记忆
- 智能压缩重复内容
- 定期整合机制

### 检索优化
- 多级索引结构
- 缓存热门查询
- 并行检索支持

### 存储优化
- 分层存储策略
- 压缩算法
- 异步写入

## 扩展建议

### 存储后端
- Redis/数据库存储
- 向量数据库集成
- 分布式存储支持

### 增强功能
- 向量嵌入相似度
- 时间衰减算法
- 情感分析标签

### 集成扩展
- 更多LLM框架支持
- 实时同步机制
- 多智能体共享记忆

## 总结

这个记忆系统为AI智能体提供了接近人类的记忆能力，包括：

- **短期记忆**: 临时信息处理
- **长期记忆**: 持久知识存储
- **工作记忆**: 当前任务上下文
- **过程记忆**: 技能和操作步骤

通过智能的检索、评分和管理机制，系统能够在保持高性能的同时提供个性化的交互体验。模块化的设计使其易于集成到各种AI应用中，并可灵活扩展以满足不同需求。

这个实现展示了如何将认知科学的记忆概念应用到AI系统中，为构建更智能、更有记忆力的AI助手提供了强大的基础架构。