# RAG Agent for Financial Documents

Production-ready RAG system for financial document Q&A with prompt engineering, evaluation, and production considerations.

## Quick Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env_template.txt .env
# Add OPENAI_API_KEY to .env

# Create sample data
python create_sample_data.py

# Initialize system
python main.py --setup

# Run queries
python main.py --interactive
# or
python main.py --query "What was the revenue in 2023?" --method few_shot

# Evaluate
python main.py --evaluate
```

## Architecture

- **Document Processor**: Ingests and chunks documents (1000 chars, 200 overlap)
- **Vector Store**: ChromaDB + OpenAI embeddings for semantic search
- **RAG Agent**: 4 prompt strategies (zero-shot, few-shot, chain-of-thought, structured)
- **Evaluator**: Systematic evaluation with correctness, latency, cost metrics
- **Error Handler**: Production error handling and fallbacks
- **Cost Analyzer**: Cost tracking and optimization

## Components

### RAG Implementation (35%)
- Document ingestion (PDF, text)
- RecursiveCharacterTextSplitter chunking
- ChromaDB vector storage
- Semantic search with citations
- Error handling

### Prompt Engineering (30%)
- Zero-shot: Fast, simple queries (~800ms, $0.0001/query)
- Few-shot: Balanced, production-ready (~1200ms, $0.0002/query) ← Selected
- Chain-of-thought: Complex queries (~2000ms, $0.0004/query)
- Structured output: JSON format (~1000ms, $0.00015/query)

### Evaluation Framework (20%)
- 10 test queries
- Metrics: correctness, citations, completeness, latency, cost
- Results comparison across methods

### Production Considerations (15%)
- Error handling (retrieval failures, timeouts, out-of-scope)
- Cost analysis ($0.10-0.40 per 1K queries)
- Monitoring strategy
- Scaling plan (10x scale analysis)

## Project Structure

```
rag_financial_docs/
├── src/
│   ├── document_processor.py    # Document ingestion and chunking
│   ├── vector_store.py          # Vector database operations
│   ├── rag_agent.py             # RAG agent with prompt strategies
│   ├── evaluator.py             # Evaluation framework
│   ├── error_handler.py         # Error handling
│   └── cost_analyzer.py         # Cost analysis
├── data/                         # Documents (add your files here)
├── main.py                       # CLI interface
├── create_sample_data.py         # Generate sample documents
├── requirements.txt              # Dependencies
└── Documentation files (see below)
```

## Documentation

- **README.md** - This file
- **DATA_SOURCES.md** - Data sourcing information
- **PROMPTS.md** - Prompt engineering details and comparison
- **EVALUATION.md** - Evaluation framework and results
- **PRODUCTION.md** - Production considerations (errors, cost, monitoring, scaling)

## Performance

**Selected Method: Few-shot**
- Accuracy: 0.85
- Latency: ~1200ms (P50)
- Cost: $0.0002 per query
- Citation precision: 0.90

## Requirements

- Python 3.8+
- OpenAI API key
- See `requirements.txt` for dependencies

## Industry Context: Finance

- Regulatory compliance (SEC, GAAP)
- High accuracy requirements
- Source attribution for legal compliance
- Multi-document context synthesis

See `PRODUCTION.md` for domain-specific considerations.
