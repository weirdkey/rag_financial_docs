"""
Main script to run the RAG agent system.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_agent import RAGAgent
from src.evaluator import Evaluator
from src.cost_analyzer import CostAnalyzer

load_dotenv()


def setup_rag_system(data_directory: str = "./data", rebuild: bool = False):
    """
    Set up the RAG system by processing documents and creating vector store.
    
    Args:
        data_directory: Directory containing documents
        rebuild: Whether to rebuild the vector store
    """
    print("Setting up RAG system...")
    
    # Initialize components
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    vector_store = VectorStore()
    
    # Rebuild if requested
    if rebuild:
        print("Rebuilding vector store...")
        vector_store.delete_collection()
        vector_store = VectorStore()
    
    # Check if vector store already has documents
    collection_info = vector_store.get_collection_info()
    if collection_info.get('document_count', 0) > 0 and not rebuild:
        print(f"Vector store already contains {collection_info['document_count']} documents.")
        print("Use rebuild=True to rebuild the vector store.")
        return vector_store
    
    # Process documents
    data_path = Path(data_directory)
    if not data_path.exists():
        print(f"Data directory {data_directory} does not exist. Please add documents.")
        return None
    
    print(f"Processing documents from {data_directory}...")
    documents = processor.process_document(data_directory) if data_path.is_file() else processor.process_directory(data_directory)
    
    if not documents:
        print("No documents found to process.")
        return None
    
    print(f"Processed {len(documents)} document chunks.")
    
    # Add to vector store
    print("Adding documents to vector store...")
    vector_store.add_documents(documents)
    
    print("RAG system setup complete!")
    print(f"Chunking strategy: {processor.get_chunking_strategy_info()}")
    print(f"Vector store info: {vector_store.get_collection_info()}")
    
    return vector_store


def run_interactive_query(vector_store: VectorStore):
    """
    Run interactive query interface.
    
    Args:
        vector_store: Initialized vector store
    """
    agent = RAGAgent(vector_store)
    
    print("\n" + "="*60)
    print("Interactive RAG Query Interface")
    print("="*60)
    print("Enter your questions (type 'exit' to quit, 'methods' to see available methods)")
    print()
    
    while True:
        query = input("Query: ").strip()
        
        if query.lower() == 'exit':
            break
        elif query.lower() == 'methods':
            print("\nAvailable methods:")
            print("  - zero_shot: Direct answer without examples")
            print("  - few_shot: Answer with examples")
            print("  - chain_of_thought: Step-by-step reasoning")
            print("  - structured_output: JSON-formatted answer")
            print()
            continue
        elif not query:
            continue
        
        # Ask for method
        method = input("Method (zero_shot/few_shot/chain_of_thought/structured_output) [zero_shot]: ").strip() or "zero_shot"
        
        if method not in ['zero_shot', 'few_shot', 'chain_of_thought', 'structured_output']:
            print("Invalid method. Using zero_shot.")
            method = 'zero_shot'
        
        # Execute query
        print(f"\nExecuting query with {method} method...")
        method_map = {
            'zero_shot': agent.query_zero_shot,
            'few_shot': agent.query_few_shot,
            'chain_of_thought': agent.query_chain_of_thought,
            'structured_output': agent.query_structured_output
        }
        
        result = method_map[method](query)
        
        # Display results
        print("\n" + "-"*60)
        print("Answer:")
        print(result.get('answer', 'No answer generated'))
        print("\nCitations:")
        for citation in result.get('citations', []):
            print(f"  [{citation['index']}] {citation['source']} (Chunk {citation['chunk_index']})")
        print(f"\nLatency: {result.get('latency_ms', 0):.2f} ms")
        print(f"Retrieved documents: {result.get('retrieved_docs', 0)}")
        print("-"*60 + "\n")


def run_evaluation(vector_store: VectorStore):
    """
    Run evaluation on test set.
    
    Args:
        vector_store: Initialized vector store
    """
    print("\nRunning evaluation...")
    
    agent = RAGAgent(vector_store)
    evaluator = Evaluator(agent)
    
    # Define test queries (these should be customized based on your documents)
    test_queries = [
        {
            'query': 'What are the key financial metrics discussed?',
            'expected_keywords': ['revenue', 'profit', 'assets', 'financial'],
            'expected_answer': 'financial metrics'
        },
        {
            'query': 'What is the revenue growth rate?',
            'expected_keywords': ['revenue', 'growth', 'rate', 'percent'],
            'expected_answer': 'revenue growth'
        },
        {
            'query': 'What are the main risks mentioned?',
            'expected_keywords': ['risk', 'uncertainty', 'challenge'],
            'expected_answer': 'risks'
        }
    ]
    
    # Run evaluation
    methods = ['zero_shot', 'few_shot', 'chain_of_thought']
    results = evaluator.evaluate_test_set(test_queries, methods)
    
    # Display results
    print("\n" + "="*60)
    print("Evaluation Results")
    print("="*60)
    
    for method, metrics in results['aggregated'].items():
        print(f"\n{method.upper()}:")
        print(f"  Success Rate: {metrics['success_rate']*100:.1f}%")
        print(f"  Avg Latency: {metrics['avg_latency_ms']:.2f} ms")
        print(f"  Avg Cost: ${metrics['avg_cost_usd']:.6f} per query")
        print(f"  Cost per 1K queries: ${metrics['cost_per_1k_queries_usd']:.2f}")
        if metrics.get('avg_correctness') is not None:
            print(f"  Avg Correctness: {metrics['avg_correctness']*100:.1f}%")
        print(f"  Avg Citation Precision: {metrics['avg_citation_precision']*100:.1f}%")
    
    # Cost analysis
    print("\n" + "="*60)
    print("Cost Analysis")
    print("="*60)
    
    cost_analyzer = CostAnalyzer()
    cost_analysis = cost_analyzer.analyze_cost_drivers(results['individual_results'])
    
    print(f"Total Queries: {cost_analysis['total_queries']}")
    print(f"Avg Cost per Query: ${cost_analysis['avg_cost_per_query_usd']:.6f}")
    print(f"Cost per 1K Queries: ${cost_analysis['cost_per_1k_queries_usd']:.2f}")
    print(f"Main Cost Driver: {cost_analysis['main_cost_driver']}")
    
    # Optimization recommendations
    recommendations = cost_analyzer.generate_optimization_recommendations(cost_analysis)
    print("\nOptimization Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['strategy'].replace('_', ' ').title()}")
        print(f"   {rec['description']}")
        print(f"   Potential Savings: {rec['potential_savings']}")
    
    print(f"\nResults saved to: {results['output_file']}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='RAG Agent System')
    parser.add_argument('--setup', action='store_true', help='Set up RAG system (process documents)')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild vector store')
    parser.add_argument('--query', type=str, help='Run a single query')
    parser.add_argument('--method', type=str, default='zero_shot', 
                       choices=['zero_shot', 'few_shot', 'chain_of_thought', 'structured_output'],
                       help='Query method to use')
    parser.add_argument('--interactive', action='store_true', help='Run interactive query interface')
    parser.add_argument('--evaluate', action='store_true', help='Run evaluation on test set')
    parser.add_argument('--data-dir', type=str, default='./data', help='Data directory path')
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in your .env file or environment.")
        return
    
    # Setup if requested
    if args.setup or args.rebuild:
        vector_store = setup_rag_system(args.data_dir, rebuild=args.rebuild)
        if not vector_store:
            return
    else:
        # Try to load existing vector store
        try:
            vector_store = VectorStore()
            collection_info = vector_store.get_collection_info()
            if collection_info.get('document_count', 0) == 0:
                print("Vector store is empty. Run with --setup to process documents.")
                return
        except Exception as e:
            print(f"Error loading vector store: {e}")
            print("Run with --setup to process documents first.")
            return
    
    # Run queries
    if args.query:
        agent = RAGAgent(vector_store)
        method_map = {
            'zero_shot': agent.query_zero_shot,
            'few_shot': agent.query_few_shot,
            'chain_of_thought': agent.query_chain_of_thought,
            'structured_output': agent.query_structured_output
        }
        result = method_map[args.method](args.query)
        print("\nAnswer:", result.get('answer', 'No answer'))
        print("\nCitations:")
        for citation in result.get('citations', []):
            print(f"  [{citation['index']}] {citation['source']}")
    elif args.interactive:
        run_interactive_query(vector_store)
    elif args.evaluate:
        run_evaluation(vector_store)
    else:
        print("No action specified. Use --setup, --query, --interactive, or --evaluate")
        parser.print_help()


if __name__ == "__main__":
    main()

