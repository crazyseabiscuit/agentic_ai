# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI experimentation repository focused on large language model applications, particularly RAG (Retrieval-Augmented Generation) systems, financial analysis, and multi-agent frameworks. The repository contains multiple case studies and implementations including:

- RAG systems for financial document analysis
- Multi-agent investment research assistants
- Model fine-tuning experiments (Qwen2.5)
- LangChain-based applications
- Financial Q&A systems
- Document processing and analysis pipelines

## Development Environment

### Technology Stack
- **Python**: >=3.10
- **Core Frameworks**: LangChain, LangGraph, Qwen-Agent, OpenAI API, DashScope
- **ML Libraries**: PyTorch, Transformers, PEFT, TRL
- **Vector Databases**: FAISS-CPU, ChromaDB, Qdrant
- **Document Processing**: PyPDF2, BeautifulSoup4, Docling (commented due to conflicts)
- **Web/API**: FastAPI, Gradio
- **Data Processing**: Pandas, NumPy, Matplotlib

### Package Management
The project uses `pyproject.toml` for dependency management with hatchling as the build backend. Dependencies are managed via pip/uv.

**Common Commands:**
```bash
# Install dependencies
pip install -e .
# or
uv sync

# Run main pipeline (RAG-cy2 project)
cd RAG-cy2
python main.py --help

# Process PDF reports
python main.py parse-pdfs --parallel --chunk-size 2 --max-workers 10

# Process questions
python main.py process-questions --config max

# Install Claude Code (using provided script)
./claude_code_prod.sh
```

## Key Components

### RAG Pipeline (RAG-cy2)
The most sophisticated component is the RAG pipeline for financial document analysis:
- **Location**: `RAG-cy2/`
- **Main Entry**: `RAG-cy2/main.py` (CLI interface) and `RAG-cy2/src/pipeline.py` (core logic)
- **Pipeline Stages**:
  1. PDF parsing and markdown conversion
  2. Document chunking and preprocessing
  3. Vector database creation (FAISS)
  4. Question processing and retrieval
  5. LLM-based answer generation

### Multi-Agent Systems
- **Investment Research**: `CASE-投研报告-Qwen-Agent/` - Multi-agent system for financial research
- **Wealth Advisor**: `CASE-投顾AI助手（混合式）/` - Hybrid wealth management advisor
- **Deliberative Research**: `CASE-智能投研助手（深思熟虑）/` - Deep thinking research assistant
- **Fund QA**: `CASE-私募基金运作指引问答助手（反应式）/` - Reactive Q&A system

### Model Fine-tuning
- **Qwen2.5 Experiments**: `模型微调/` and `CASE-Qwen2.5微调/`
- **GRPO Reasoning**: `CASE-GRPO-R1-Reasoning/`
- **Medical Fine-tuning**: Specialized medical domain adaptation

### LangChain Applications
- **Basic Chains**: `CASE-LangChain使用/` - Various LLMChain implementations
- **SQL Agents**: `Case-SQL-LangChain/` - Database interaction agents
- **Tool Chains**: `CASE-工具链组合/` - Custom tool compositions

## Architecture Patterns

### Pipeline Configuration
The RAG system uses a sophisticated configuration system in `RAG-cy2/src/pipeline.py`:
- `PipelineConfig`: Manages file paths and directory structure
- `RunConfig`: Controls pipeline behavior (parallel processing, model selection, etc.)
- Predefined configurations: `base`, `pdr`, `max` with different optimization levels

### Multi-Agent Design
Agents use structured patterns with:
- Role-based specializations (researcher, planner, coordinator, reporter)
- Memory management with JSON-based persistence
- Tool integration for code execution and document parsing
- LangGraph-based workflow orchestration

### Data Processing Patterns
- **Document Processing**: PDF → Markdown → Chunking → Vectorization
- **Parallel Processing**: Multi-threaded PDF parsing and table serialization
- **Retrieval Strategies**: Vector search + BM25 + Parent Document Retrieval
- **Reranking**: LLM-based context relevance filtering

## File Structure Conventions

### Case Studies
Each case study is self-contained in its own directory with:
- `CASE-*` prefix for experimental cases
- Descriptive Chinese names indicating the focus area
- Independent requirements and dependencies

### Data Organization
- **PDF Reports**: Stored in `pdf_reports/` subdirectories
- **Vector Databases**: `databases/vector_dbs/`
- **Chunked Documents**: `databases/chunked_reports/`
- **Results**: JSON files with timestamps (`answers_*.json`)

### Workspace Tools
- **Document Parsers**: `workspace/tools/doc_parser/` and `workspace/tools/simple_doc_parser/`
- **Code Execution**: `workspace/tools/code_interpreter/` with kernel management
- **Cached Data**: Processed documents and intermediate results

## Development Notes

### API Integration
- **Qwen API**: Primary model provider via DashScope
- **Rate Limiting**: Qwen-Turbo limited to 500 QPM and 500K tokens per minute
- **Fallback Models**: OpenAI GPT models as alternatives

### Performance Considerations
- **Parallel Processing**: Configurable worker counts for CPU-bound tasks
- **Memory Management**: Streaming processing for large documents
- **Vector Search**: FAISS for efficient similarity search
- **Caching**: Disk cache for intermediate results

### Configuration Management
- **Environment Variables**: Use `.env` files for API keys
- **Model Selection**: Configurable via `RunConfig.answering_model`
- **Pipeline Variants**: Different configurations for performance vs accuracy trade-offs

## Common Development Tasks

### Adding New Case Studies
1. Create new directory with `CASE-` prefix
2. Add requirements.txt if needed
3. Follow existing patterns for agent/pipeline implementation
4. Update main dependencies in pyproject.toml if necessary

### Extending RAG Pipeline
1. Modify `RAG-cy2/src/pipeline.py` for new pipeline stages
2. Add new configuration options to `RunConfig`
3. Update CLI commands in `RAG-cy2/main.py`
4. Test with existing financial documents

### Model Fine-tuning
1. Use existing fine-tuning scripts as templates
2. Prepare training data in appropriate format
3. Configure model parameters and training settings
4. Monitor with Weights & Biases integration

## Claude Code Integration

The repository includes a setup script (`claude_code_prod.sh`) for Claude Code with:
- Node.js and npm installation
- Claude Code package installation
- Configuration for Zhipu AI API integration
- Authentication and endpoint setup