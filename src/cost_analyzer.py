"""
Cost Analysis Module
Analyzes and optimizes costs for RAG system.
"""

import json
from typing import Dict, Any, List
from pathlib import Path
import tiktoken


class CostAnalyzer:
    """Analyzes costs and provides optimization recommendations."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize cost analyzer.
        
        Args:
            model: Model name for pricing
        """
        self.model = model
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
        # Pricing per 1M tokens (as of 2024)
        self.pricing = {
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
            "gpt-4o": {"prompt": 2.50, "completion": 10.00},
            "gpt-4": {"prompt": 30.00, "completion": 60.00},
            "text-embedding-3-small": {"prompt": 0.02, "completion": 0.0}
        }
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def calculate_query_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        embedding_tokens: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate cost for a single query.
        
        Args:
            prompt_tokens: Prompt tokens
            completion_tokens: Completion tokens
            embedding_tokens: Embedding tokens (for retrieval)
            
        Returns:
            Cost breakdown dictionary
        """
        model_pricing = self.pricing.get(self.model, self.pricing["gpt-4o-mini"])
        embedding_pricing = self.pricing.get("text-embedding-3-small", {"prompt": 0.02, "completion": 0.0})
        
        prompt_cost = (prompt_tokens / 1_000_000) * model_pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * model_pricing["completion"]
        embedding_cost = (embedding_tokens / 1_000_000) * embedding_pricing["prompt"]
        
        total_cost = prompt_cost + completion_cost + embedding_cost
        
        return {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'embedding_tokens': embedding_tokens,
            'prompt_cost_usd': prompt_cost,
            'completion_cost_usd': completion_cost,
            'embedding_cost_usd': embedding_cost,
            'total_cost_usd': total_cost,
            'cost_per_1k_queries_usd': total_cost * 1000
        }
    
    def analyze_cost_drivers(
        self,
        evaluation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze cost drivers from evaluation results.
        
        Args:
            evaluation_results: List of evaluation result dictionaries
            
        Returns:
            Cost analysis dictionary
        """
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_embedding_tokens = 0
        total_cost = 0.0
        
        for result in evaluation_results:
            if 'cost' in result:
                cost_info = result['cost']
                total_prompt_tokens += cost_info.get('prompt_tokens', 0)
                total_completion_tokens += cost_info.get('completion_tokens', 0)
                total_cost += cost_info.get('total_cost_usd', 0)
        
        avg_prompt_tokens = total_prompt_tokens / len(evaluation_results) if evaluation_results else 0
        avg_completion_tokens = total_completion_tokens / len(evaluation_results) if evaluation_results else 0
        avg_cost = total_cost / len(evaluation_results) if evaluation_results else 0
        
        # Identify cost drivers
        prompt_percentage = (total_prompt_tokens / (total_prompt_tokens + total_completion_tokens) * 100) if (total_prompt_tokens + total_completion_tokens) > 0 else 0
        completion_percentage = 100 - prompt_percentage
        
        return {
            'total_queries': len(evaluation_results),
            'total_cost_usd': total_cost,
            'avg_cost_per_query_usd': avg_cost,
            'cost_per_1k_queries_usd': avg_cost * 1000,
            'avg_prompt_tokens': avg_prompt_tokens,
            'avg_completion_tokens': avg_completion_tokens,
            'prompt_cost_percentage': prompt_percentage,
            'completion_cost_percentage': completion_percentage,
            'main_cost_driver': 'prompt' if prompt_percentage > completion_percentage else 'completion'
        }
    
    def generate_optimization_recommendations(
        self,
        cost_analysis: Dict[str, Any],
        target_cost_reduction: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Generate cost optimization recommendations.
        
        Args:
            cost_analysis: Cost analysis dictionary
            target_cost_reduction: Target cost reduction (0.0 to 1.0)
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        current_cost = cost_analysis.get('avg_cost_per_query_usd', 0)
        target_cost = current_cost * (1 - target_cost_reduction)
        
        # Recommendation 1: Reduce prompt size
        if cost_analysis.get('prompt_cost_percentage', 0) > 60:
            recommendations.append({
                'strategy': 'reduce_prompt_size',
                'description': 'Reduce context window size or use more efficient chunking',
                'potential_savings': f"{cost_analysis.get('prompt_cost_percentage', 0) * 0.3:.1f}%",
                'implementation': 'Reduce top_k retrieval, use smaller chunks, or implement query compression'
            })
        
        # Recommendation 2: Use cheaper model
        if current_cost > 0.01:  # If cost is significant
            recommendations.append({
                'strategy': 'use_cheaper_model',
                'description': 'Switch to gpt-4o-mini for non-critical queries',
                'potential_savings': '60-80%',
                'implementation': 'Use model routing based on query complexity or user tier'
            })
        
        # Recommendation 3: Cache common queries
        recommendations.append({
            'strategy': 'implement_caching',
            'description': 'Cache frequent queries and their responses',
            'potential_savings': '30-50% for repeated queries',
            'implementation': 'Use Redis or in-memory cache with TTL based on document update frequency'
        })
        
        # Recommendation 4: Optimize chunking
        recommendations.append({
            'strategy': 'optimize_chunking',
            'description': 'Reduce chunk overlap and optimize chunk size',
            'potential_savings': '10-20%',
            'implementation': 'Reduce chunk_overlap from 200 to 100, optimize chunk_size based on average query length'
        })
        
        # Recommendation 5: Batch processing
        recommendations.append({
            'strategy': 'batch_processing',
            'description': 'Batch multiple queries when possible',
            'potential_savings': '15-25%',
            'implementation': 'Collect queries and process in batches to reduce API overhead'
        })
        
        return recommendations
    
    def estimate_10x_scale_costs(
        self,
        current_cost_per_1k: float,
        current_volume: int = 1000
    ) -> Dict[str, Any]:
        """
        Estimate costs at 10x scale.
        
        Args:
            current_cost_per_1k: Current cost per 1000 queries
            current_volume: Current query volume
            
        Returns:
            Scaling cost analysis
        """
        scaled_volume = current_volume * 10
        scaled_cost = (current_cost_per_1k / 1000) * scaled_volume
        
        # Identify what would break first
        bottlenecks = []
        
        if scaled_volume > 10000:
            bottlenecks.append({
                'component': 'Vector Database',
                'issue': 'Query throughput limits',
                'solution': 'Implement read replicas or sharding'
            })
        
        if scaled_cost > 1000:
            bottlenecks.append({
                'component': 'LLM API',
                'issue': 'Cost becomes prohibitive',
                'solution': 'Implement caching, model routing, or rate limiting'
            })
        
        bottlenecks.append({
            'component': 'Embedding Generation',
            'issue': 'Embedding API rate limits',
            'solution': 'Cache embeddings, use batch API, or pre-compute embeddings'
        })
        
        return {
            'current_volume': current_volume,
            'scaled_volume': scaled_volume,
            'current_cost_per_1k_usd': current_cost_per_1k,
            'scaled_monthly_cost_usd': scaled_cost * 30,  # Assuming daily volume
            'scaled_daily_cost_usd': scaled_cost,
            'bottlenecks': bottlenecks,
            'optimization_priority': 'cost' if scaled_cost > 1000 else 'throughput'
        }

