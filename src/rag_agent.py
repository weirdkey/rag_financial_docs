import os
import time
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv

from .vector_store import VectorStore

load_dotenv()


class RAGAgent:
    """RAG agent with multiple prompt strategies for financial document Q&A."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0,
        max_tokens: int = 1000
    ):
        """Initialize RAG agent with vector store and LLM configuration."""
        self.vector_store = vector_store
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=api_key
        )
    
    def _format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents as context string."""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'Unknown')
            chunk_idx = doc.metadata.get('chunk_index', '?')
            context_parts.append(
                f"[Source {i}: {source}, Chunk {chunk_idx}]\n{doc.page_content}"
            )
        return "\n\n".join(context_parts)
    
    def _get_citations(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Extract citation information from documents."""
        citations = []
        for i, doc in enumerate(documents, 1):
            citations.append({
                'index': i,
                'source': doc.metadata.get('source', 'Unknown'),
                'chunk_index': doc.metadata.get('chunk_index', '?'),
                'preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        return citations
    
    def query_zero_shot(
        self,
        query: str,
        top_k: int = 5,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """Zero-shot prompting: direct answer without examples."""
        start_time = time.time()
        
        # Retrieve relevant documents
        documents = self.vector_store.similarity_search(query, k=top_k)
        if not documents:
            return {
                'answer': "I couldn't find relevant information to answer your question.",
                'citations': [],
                'error': 'No documents retrieved',
                'latency_ms': (time.time() - start_time) * 1000
            }
        
        # Format context
        context = self._format_context(documents)
        
        # Zero-shot prompt
        system_prompt = """You are a financial document analysis assistant. 
Answer questions based ONLY on the provided context from financial documents.
Be precise, cite specific sources, and if information is not in the context, say so clearly.
Format your answer clearly with proper structure."""
        
        human_prompt = """Context from financial documents:
{context}

Question: {query}

Answer the question based on the context above. If the answer cannot be determined from the context, state that clearly."""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt)
        ])
        
        # Generate response
        messages = prompt.format_messages(context=context, query=query)
        response = self.llm.invoke(messages)
        answer = response.content
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            'answer': answer,
            'latency_ms': latency_ms,
            'retrieved_docs': len(documents)
        }
        
        if include_citations:
            result['citations'] = self._get_citations(documents)
        
        return result
    
    def query_few_shot(
        self,
        query: str,
        top_k: int = 5,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """Few-shot prompting: includes example Q&A pairs in prompt."""
        start_time = time.time()
        
        # Retrieve relevant documents
        documents = self.vector_store.similarity_search(query, k=top_k)
        if not documents:
            return {
                'answer': "I couldn't find relevant information to answer your question.",
                'citations': [],
                'error': 'No documents retrieved',
                'latency_ms': (time.time() - start_time) * 1000
            }
        
        # Format context
        context = self._format_context(documents)
        
        # Few-shot prompt with examples
        system_prompt = """You are a financial document analysis assistant.
Answer questions based ONLY on the provided context from financial documents.

Example 1:
Context: [Source 1: annual_report.pdf, Chunk 3]
Revenue of $10M was reported in Q3 2023, representing a 15% increase year-over-year.

Question: What was the revenue in Q3 2023?
Answer: Based on Source 1, revenue of $10M was reported in Q3 2023, representing a 15% increase year-over-year.

Example 2:
Context: [Source 1: financial_statement.pdf, Chunk 1]
Total assets increased from $50M to $65M between 2022 and 2023.

Question: How did total assets change?
Answer: According to Source 1, total assets increased from $50M to $65M between 2022 and 2023, representing a $15M increase.

Now answer the user's question following the same format."""
        
        human_prompt = """Context from financial documents:
{context}

Question: {query}

Answer the question based on the context above, following the format shown in the examples. Cite your sources."""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt)
        ])
        
        # Generate response
        messages = prompt.format_messages(context=context, query=query)
        response = self.llm.invoke(messages)
        answer = response.content
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            'answer': answer,
            'latency_ms': latency_ms,
            'retrieved_docs': len(documents)
        }
        
        if include_citations:
            result['citations'] = self._get_citations(documents)
        
        return result
    
    def query_chain_of_thought(
        self,
        query: str,
        top_k: int = 5,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """Chain-of-thought prompting: requires step-by-step reasoning."""
        start_time = time.time()
        
        # Retrieve relevant documents
        documents = self.vector_store.similarity_search(query, k=top_k)
        if not documents:
            return {
                'answer': "I couldn't find relevant information to answer your question.",
                'citations': [],
                'error': 'No documents retrieved',
                'latency_ms': (time.time() - start_time) * 1000
            }
        
        # Format context
        context = self._format_context(documents)
        
        # Chain-of-thought prompt
        system_prompt = """You are a financial document analysis assistant.
Answer questions by thinking through the problem step by step.
1. First, identify what information is needed to answer the question
2. Then, search through the provided context for relevant information
3. Analyze and synthesize the information
4. Finally, provide a clear answer with citations

Be methodical and show your reasoning."""
        
        human_prompt = """Context from financial documents:
{context}

Question: {query}

Think through this step by step:
1. What information do I need to answer this question?
2. What relevant information is in the context?
3. How do I synthesize this information?
4. What is my final answer?

Provide your reasoning and answer."""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt)
        ])
        
        # Generate response
        messages = prompt.format_messages(context=context, query=query)
        response = self.llm.invoke(messages)
        answer = response.content
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            'answer': answer,
            'latency_ms': latency_ms,
            'retrieved_docs': len(documents)
        }
        
        if include_citations:
            result['citations'] = self._get_citations(documents)
        
        return result
    
    def query_structured_output(
        self,
        query: str,
        top_k: int = 5,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """Structured output prompting: requests JSON-formatted response."""
        start_time = time.time()
        
        # Retrieve relevant documents
        documents = self.vector_store.similarity_search(query, k=top_k)
        if not documents:
            return {
                'answer': "I couldn't find relevant information to answer your question.",
                'citations': [],
                'error': 'No documents retrieved',
                'latency_ms': (time.time() - start_time) * 1000
            }
        
        # Format context
        context = self._format_context(documents)
        
        # Structured output prompt
        system_prompt = """You are a financial document analysis assistant.
Answer questions based on the provided context and format your response as JSON with the following structure:
{{
    "answer": "Your answer to the question",
    "confidence": "high/medium/low",
    "key_facts": ["fact1", "fact2", ...],
    "sources": ["source1", "source2", ...]
}}"""
        
        human_prompt = """Context from financial documents:
{context}

Question: {query}

Provide your answer in the specified JSON format."""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt)
        ])
        
        # Generate response
        messages = prompt.format_messages(context=context, query=query)
        response = self.llm.invoke(messages)
        answer = response.content
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            'answer': answer,
            'latency_ms': latency_ms,
            'retrieved_docs': len(documents)
        }
        
        if include_citations:
            result['citations'] = self._get_citations(documents)
        
        return result

