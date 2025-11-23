"""
Error Handling Module
Handles various error scenarios in production.
"""

import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGError(Exception):
    """Base exception for RAG system errors."""
    pass


class RetrievalError(RAGError):
    """Error during document retrieval."""
    pass


class GenerationError(RAGError):
    """Error during LLM generation."""
    pass


class TimeoutError(RAGError):
    """Operation timeout error."""
    pass


class ErrorHandler:
    """Handles errors and provides fallback strategies."""
    
    @staticmethod
    def handle_retrieval_failure(
        query: str,
        error: Exception,
        fallback_strategy: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Handle retrieval failure.
        
        Args:
            query: Original query
            error: Exception that occurred
            fallback_strategy: Optional fallback function
            
        Returns:
            Error response dictionary
        """
        logger.error(f"Retrieval failed for query: {query}. Error: {str(error)}")
        
        if fallback_strategy:
            try:
                return fallback_strategy(query)
            except Exception as fallback_error:
                logger.error(f"Fallback strategy also failed: {str(fallback_error)}")
        
        return {
            'answer': "I encountered an error while searching for information. Please try rephrasing your question or contact support if the issue persists.",
            'error': 'retrieval_failure',
            'error_message': str(error),
            'citations': []
        }
    
    @staticmethod
    def handle_llm_timeout(
        query: str,
        timeout_seconds: float = 30.0,
        fallback_strategy: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Handle LLM timeout.
        
        Args:
            query: Original query
            timeout_seconds: Timeout threshold
            fallback_strategy: Optional fallback function
            
        Returns:
            Timeout response dictionary
        """
        logger.warning(f"LLM timeout for query: {query} (>{timeout_seconds}s)")
        
        if fallback_strategy:
            try:
                return fallback_strategy(query)
            except Exception as fallback_error:
                logger.error(f"Fallback strategy failed: {str(fallback_error)}")
        
        return {
            'answer': "The request took too long to process. Please try a simpler or more specific question.",
            'error': 'timeout',
            'timeout_seconds': timeout_seconds,
            'citations': []
        }
    
    @staticmethod
    def handle_out_of_scope_query(
        query: str,
        scope_description: str = "financial documents"
    ) -> Dict[str, Any]:
        """
        Handle queries outside system scope.
        
        Args:
            query: Original query
            scope_description: Description of system scope
            
        Returns:
            Out-of-scope response dictionary
        """
        logger.info(f"Out-of-scope query detected: {query}")
        
        return {
            'answer': f"I can only answer questions about {scope_description}. Your question appears to be outside this scope. Please rephrase your question to focus on {scope_description}.",
            'error': 'out_of_scope',
            'scope': scope_description,
            'citations': []
        }
    
    @staticmethod
    def handle_malformed_input(
        query: str,
        error: Exception
    ) -> Dict[str, Any]:
        """
        Handle malformed input.
        
        Args:
            query: Original query
            error: Exception that occurred
            
        Returns:
            Malformed input response dictionary
        """
        logger.warning(f"Malformed input detected: {query}. Error: {str(error)}")
        
        return {
            'answer': "I couldn't understand your question. Please try rephrasing it or breaking it into simpler parts.",
            'error': 'malformed_input',
            'error_message': str(error),
            'citations': []
        }
    
    @staticmethod
    def handle_empty_response(
        query: str,
        retrieved_docs: int = 0
    ) -> Dict[str, Any]:
        """
        Handle empty or no response.
        
        Args:
            query: Original query
            retrieved_docs: Number of documents retrieved
            
        Returns:
            Empty response dictionary
        """
        logger.info(f"Empty response for query: {query} (retrieved {retrieved_docs} docs)")
        
        if retrieved_docs == 0:
            return {
                'answer': "I couldn't find any relevant information in the documents to answer your question. Please try rephrasing or asking about a different topic.",
                'error': 'no_relevant_docs',
                'retrieved_docs': 0,
                'citations': []
            }
        else:
            return {
                'answer': "I found some documents but couldn't generate a meaningful answer. The documents may not contain the specific information you're looking for.",
                'error': 'empty_response',
                'retrieved_docs': retrieved_docs,
                'citations': []
            }
    
    @staticmethod
    def with_error_handling(
        func: Callable,
        timeout_seconds: float = 30.0,
        scope_check: Optional[Callable] = None
    ) -> Callable:
        """
        Decorator to add error handling to a function.
        
        Args:
            func: Function to wrap
            timeout_seconds: Timeout threshold
            scope_check: Optional function to check if query is in scope
            
        Returns:
            Wrapped function with error handling
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Check scope if function provided
                if scope_check and 'query' in kwargs:
                    if not scope_check(kwargs['query']):
                        return ErrorHandler.handle_out_of_scope_query(kwargs['query'])
                
                # Execute with timeout
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if elapsed > timeout_seconds:
                    return ErrorHandler.handle_llm_timeout(
                        kwargs.get('query', 'unknown'),
                        timeout_seconds
                    )
                
                # Check for empty response
                if not result or not result.get('answer'):
                    return ErrorHandler.handle_empty_response(
                        kwargs.get('query', 'unknown'),
                        result.get('retrieved_docs', 0) if result else 0
                    )
                
                return result
                
            except TimeoutError:
                return ErrorHandler.handle_llm_timeout(
                    kwargs.get('query', 'unknown'),
                    timeout_seconds
                )
            except RetrievalError as e:
                return ErrorHandler.handle_retrieval_failure(
                    kwargs.get('query', 'unknown'),
                    e
                )
            except GenerationError as e:
                return ErrorHandler.handle_retrieval_failure(
                    kwargs.get('query', 'unknown'),
                    e
                )
            except ValueError as e:
                return ErrorHandler.handle_malformed_input(
                    kwargs.get('query', 'unknown'),
                    e
            )
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                return {
                    'answer': "An unexpected error occurred. Please try again later.",
                    'error': 'unexpected_error',
                    'error_message': str(e),
                    'citations': []
                }
        
        return wrapper

