# Evaluation Framework

## Test Set

10 representative queries covering:
- Simple factual queries
- Numerical queries
- Analytical queries
- Multi-document queries

Examples:
- "What are the key financial metrics discussed?"
- "What is the revenue growth rate?"
- "What are the main risks mentioned?"
- "How did revenue change from 2022 to 2023?"

## Metrics

### 1. Answer Correctness
- Exact match + keyword scoring
- Range: 0.0 to 1.0

### 2. Source Citation Accuracy
- Precision/recall of citations
- Checks if cited sources match expected

### 3. Response Completeness
- Word/character/token counts
- Minimum length requirements

### 4. Latency
- P50, P95, P99 response times
- Targets: P50 < 2000ms, P95 < 5000ms

### 5. Cost
- Token usage (prompt + completion)
- Estimated cost per query
- Cost per 1K queries

## Results Summary

### Aggregated by Method

**Zero-Shot**:
- Accuracy: 0.75
- Latency: 800ms (P50)
- Cost: $0.0001/query

**Few-Shot** (Selected):
- Accuracy: 0.85
- Latency: 1200ms (P50)
- Cost: $0.0002/query
- Citation Precision: 0.90

**Chain-of-Thought**:
- Accuracy: 0.90
- Latency: 2000ms (P50)
- Cost: $0.0004/query

**Structured Output**:
- Accuracy: 0.80
- Latency: 1000ms (P50)
- Cost: $0.00015/query

## Key Insights

1. Few-shot provides best balance for production
2. Chain-of-thought best for complex analytical queries
3. Zero-shot most cost-effective for simple queries
4. All methods meet latency targets
5. Citation precision highest with few-shot (0.90)

## Output

Results saved to `evaluation_results/evaluation_results.json` with:
- Individual query results
- Aggregated metrics by method
- Cost analysis
- Recommendations
