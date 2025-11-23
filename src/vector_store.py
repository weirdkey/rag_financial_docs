import os
from typing import List, Dict, Any, Optional
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()


class VectorStore:
    """Vector database for semantic search using ChromaDB and OpenAI embeddings."""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "financial_docs"):
        """Initialize vector store with embeddings and ChromaDB."""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=api_key
        )
        
        # Initialize Chroma
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to vector store and persist."""
        try:
            ids = self.vectorstore.add_documents(documents)
            self.vectorstore.persist()
            return ids
        except Exception as e:
            raise RuntimeError(f"Error adding documents to vector store: {str(e)}")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Perform semantic similarity search."""
        try:
            if filter:
                results = self.vectorstore.similarity_search(
                    query, 
                    k=k,
                    filter=filter
                )
            else:
                results = self.vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            raise RuntimeError(f"Error performing similarity search: {str(e)}")
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """Perform similarity search with relevance scores."""
        try:
            if filter:
                results = self.vectorstore.similarity_search_with_score(
                    query,
                    k=k,
                    filter=filter
                )
            else:
                results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            raise RuntimeError(f"Error performing similarity search with score: {str(e)}")
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            client = chromadb.PersistentClient(path=self.persist_directory)
            client.delete_collection(name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {str(e)}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics and metadata."""
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                'collection_name': self.collection_name,
                'document_count': count,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            return {'error': str(e)}

