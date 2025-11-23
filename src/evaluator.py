"""
Evaluation Framework Module
Implements metrics and evaluation for RAG system.
"""

import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import tiktoken
from .rag_agent import RAGAgent


class Evaluator:
    """Evaluates RAG agent performance across different metrics."""
    
    def __init__(self, agent: RAGAgent, output_dir: str = "./evaluation_results"):
        """
        Initialize evaluator.
        
        Args:
            agent: RAGAgent instance to evaluate
            output_dir: Directory to save evaluation results
        """
        self.agent = agent
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.encoding = tiktoken.encoding_for_model("gpt-4")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def evaluate_answer_correctness(
        self,
        answer: str,
        expected_answer: str,
        expected_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate answer correctness.
        
        Args:
            answer: Generated answer
            expected_answer: Expected answer or answer type
            expected_keywords: Optional list of keywords that should appear
            
        Returns:
            Dictionary with correctness metrics
        """
        answer_lower = answer.lower()
        expected_lower = expected_answer.lower()
        
        # Binary correctness (exact match or contains expected)
        exact_match = expected_lower in answer_lower or answer_lower in expected_lower
        
        # Keyword-based scoring
        keyword_score = 0.0
        if expected_keywords:
            found_keywords = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
            keyword_score = found_keywords / len(expected_keywords) if expected_keywords else 0.0
        
        # Combined score
        correctness_score = 1.0 if exact_match else keyword_score
        
        return {
            'exact_match': exact_match,
            'keyword_score': keyword_score,
            'correctness_score': correctness_score,
            'found_keywords': [kw for kw in (expected_keywords or []) if kw.lower() in answer_lower],
            'missing_keywords': [kw for kw in (expected_keywords or []) if kw.lower() not in answer_lower]
        }
    
    def evaluate_source_citation_accuracy(
        self,
        citations: List[Dict[str, Any]],
        expected_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate source citation accuracy.
        
        Args:
            citations: List of citation dictionaries
            expected_sources: Optional list of expected source files
            
        Returns:
            Dictionary with citation metrics
        """
        if not citations:
            return {
                'has_citations': False,
                'citation_count': 0,
                'precision': 0.0,
                'recall': 0.0
            }
        
        citation_sources = [c.get('source', '') for c in citations]
        
        precision = 1.0
        recall = 1.0
        
        if expected_sources:
            # Check if cited sources match expected
            expected_set = set(expected_sources)
            cited_set = set(citation_sources)
            
            true_positives = len(expected_set & cited_set)
            false_positives = len(cited_set - expected_set)
            false_negatives = len(expected_set - cited_set)
            
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        
        return {
            'has_citations': True,
            'citation_count': len(citations),
            'precision': precision,
            'recall': recall,
            'cited_sources': citation_sources
        }
    
    def evaluate_response_completeness(
        self,
        answer: str,
        min_length: int = 50
    ) -> Dict[str, Any]:
        """
        Evaluate response completeness.
        
        Args:
            answer: Generated answer
            min_length: Minimum expected answer length
            
        Returns:
            Dictionary with completeness metrics
        """
        word_count = len(answer.split())
        char_count = len(answer)
        token_count = self.count_tokens(answer)
        
        is_complete = char_count >= min_length and word_count >= 10
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'token_count': token_count,
            'is_complete': is_complete,
            'completeness_score': min(1.0, char_count / min_length) if min_length > 0 else 1.0
        }
    
    def evaluate_latency(
        self,
        latency_ms: float,
        target_p50: float = 2000.0,
        target_p95: float = 5000.0
    ) -> Dict[str, Any]:
        """
        Evaluate response latency.
        
        Args:
            latency_ms: Latency in milliseconds
            target_p50: Target p50 latency
            target_p95: Target p95 latency
            
        Returns:
            Dictionary with latency metrics
        """
        meets_p50 = latency_ms <= target_p50
        meets_p95 = latency_ms <= target_p95
        
        return {
            'latency_ms': latency_ms,
            'meets_p50': meets_p50,
            'meets_p95': meets_p95,
            'target_p50': target_p50,
            'target_p95': target_p95
        }
    
    def evaluate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """
        Estimate cost based on token usage.
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            model: Model name for pricing
            
        Returns:
            Dictionary with cost metrics
        """
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
            "gpt-4o": {"prompt": 2.50, "completion": 10.00},
            "gpt-4": {"prompt": 30.00, "completion": 60.00}
        }
        
        model_pricing = pricing.get(model, pricing["gpt-4o-mini"])
        
        prompt_cost = (prompt_tokens / 1_000_000) * model_pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * model_pricing["completion"]
        total_cost = prompt_cost + completion_cost
        
        cost_per_1k_queries = total_cost * 1000
        
        return {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens,
            'prompt_cost_usd': prompt_cost,
            'completion_cost_usd': completion_cost,
            'total_cost_usd': total_cost,
            'cost_per_1k_queries_usd': cost_per_1k_queries,
            'model': model
        }
    
    def evaluate_query(
        self,
        query: str,
        method: str,
        expected_answer: Optional[str] = None,
        expected_keywords: Optional[List[str]] = None,
        expected_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single query using specified method.
        
        Args:
            query: Test query
            method: Prompt method ('zero_shot', 'few_shot', 'chain_of_thought', 'structured_output')
            expected_answer: Expected answer (optional)
            expected_keywords: Expected keywords (optional)
            expected_sources: Expected sources (optional)
            
        Returns:
            Dictionary with evaluation results
        """
        # Get method function
        method_map = {
            'zero_shot': self.agent.query_zero_shot,
            'few_shot': self.agent.query_few_shot,
            'chain_of_thought': self.agent.query_chain_of_thought,
            'structured_output': self.agent.query_structured_output
        }
        
        if method not in method_map:
            raise ValueError(f"Unknown method: {method}")
        
        query_func = method_map[method]
        
        # Execute query
        try:
            result = query_func(query, include_citations=True)
            
            if 'error' in result:
                return {
                    'query': query,
                    'method': method,
                    'error': result['error'],
                    'success': False
                }
            
            answer = result['answer']
            citations = result.get('citations', [])
            latency_ms = result.get('latency_ms', 0)
            
            # Evaluate different aspects
            correctness = self.evaluate_answer_correctness(
                answer, expected_answer or "", expected_keywords
            ) if expected_answer or expected_keywords else None
            
            citation_accuracy = self.evaluate_source_citation_accuracy(
                citations, expected_sources
            )
            
            completeness = self.evaluate_response_completeness(answer)
            latency = self.evaluate_latency(latency_ms)
            
            # Estimate token usage (approximate)
            prompt_tokens = self.count_tokens(query + str(citations))
            completion_tokens = self.count_tokens(answer)
            cost = self.evaluate_cost(prompt_tokens, completion_tokens, self.agent.model_name)
            
            return {
                'query': query,
                'method': method,
                'success': True,
                'answer': answer,
                'correctness': correctness,
                'citation_accuracy': citation_accuracy,
                'completeness': completeness,
                'latency': latency,
                'cost': cost,
                'retrieved_docs': result.get('retrieved_docs', 0)
            }
            
        except Exception as e:
            return {
                'query': query,
                'method': method,
                'error': str(e),
                'success': False
            }
    
    def evaluate_test_set(
        self,
        test_queries: List[Dict[str, Any]],
        methods: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a test set across multiple methods.
        
        Args:
            test_queries: List of test query dictionaries with 'query', 'expected_answer', etc.
            methods: List of methods to test (default: all methods)
            
        Returns:
            Dictionary with comprehensive evaluation results
        """
        if methods is None:
            methods = ['zero_shot', 'few_shot', 'chain_of_thought', 'structured_output']
        
        all_results = []
        
        for test_case in test_queries:
            query = test_case['query']
            expected_answer = test_case.get('expected_answer')
            expected_keywords = test_case.get('expected_keywords')
            expected_sources = test_case.get('expected_sources')
            
            for method in methods:
                result = self.evaluate_query(
                    query, method, expected_answer, expected_keywords, expected_sources
                )
                all_results.append(result)
        
        # Aggregate results
        aggregated = self._aggregate_results(all_results, methods)
        
        # Save results
        output_file = self.output_dir / "evaluation_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                'test_queries': test_queries,
                'methods': methods,
                'results': all_results,
                'aggregated': aggregated
            }, f, indent=2)
        
        return {
            'individual_results': all_results,
            'aggregated': aggregated,
            'output_file': str(output_file)
        }
    
    def _aggregate_results(
        self,
        results: List[Dict[str, Any]],
        methods: List[str]
    ) -> Dict[str, Any]:
        """Aggregate evaluation results by method."""
        aggregated = {}
        
        for method in methods:
            method_results = [r for r in results if r.get('method') == method and r.get('success')]
            
            if not method_results:
                continue
            
            # Aggregate metrics
            latencies = [r['latency']['latency_ms'] for r in method_results if 'latency' in r]
            costs = [r['cost']['total_cost_usd'] for r in method_results if 'cost' in r]
            correctness_scores = [
                r['correctness']['correctness_score'] 
                for r in method_results 
                if 'correctness' in r and r['correctness'] is not None
            ]
            citation_precisions = [
                r['citation_accuracy']['precision'] 
                for r in method_results 
                if 'citation_accuracy' in r
            ]
            completeness_scores = [
                r['completeness']['completeness_score'] 
                for r in method_results 
                if 'completeness' in r
            ]
            
            aggregated[method] = {
                'total_queries': len(method_results),
                'success_rate': len(method_results) / len([r for r in results if r.get('method') == method]),
                'avg_latency_ms': sum(latencies) / len(latencies) if latencies else 0,
                'p50_latency_ms': sorted(latencies)[len(latencies)//2] if latencies else 0,
                'p95_latency_ms': sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0,
                'avg_cost_usd': sum(costs) / len(costs) if costs else 0,
                'total_cost_usd': sum(costs),
                'cost_per_1k_queries_usd': (sum(costs) / len(costs) * 1000) if costs else 0,
                'avg_correctness': sum(correctness_scores) / len(correctness_scores) if correctness_scores else None,
                'avg_citation_precision': sum(citation_precisions) / len(citation_precisions) if citation_precisions else 0,
                'avg_completeness': sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
            }
        
        return aggregated

