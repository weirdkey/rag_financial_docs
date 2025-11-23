import os
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DocumentProcessor:
    """Document ingestion and chunking for vector storage."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize with chunk size and overlap parameters."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise ValueError(f"Error loading PDF {file_path}: {str(e)}")
    
    def load_text_file(self, file_path: str) -> str:
        """Load text file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error loading text file {file_path}: {str(e)}")
    
    def process_document(self, file_path: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """Process document into chunks with metadata."""
        file_path_obj = Path(file_path)
        file_ext = file_path_obj.suffix.lower()
        
        # Load document based on type
        if file_ext == '.pdf':
            text = self.load_pdf(file_path)
        elif file_ext in ['.txt', '.md']:
            text = self.load_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        if not text.strip():
            raise ValueError(f"Document {file_path} is empty or could not be extracted")
        
        # Create base metadata
        doc_metadata = {
            'source': str(file_path),
            'filename': file_path_obj.name,
            'file_type': file_ext
        }
        if metadata:
            doc_metadata.update(metadata)
        
        # Split into chunks
        chunks = self.text_splitter.create_documents(
            texts=[text],
            metadatas=[doc_metadata]
        )
        
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_index'] = i
            chunk.metadata['total_chunks'] = len(chunks)
        
        return chunks
    
    def process_directory(self, directory_path: str) -> List[Document]:
        """Process all supported documents in directory."""
        all_chunks = []
        directory = Path(directory_path)
        
        supported_extensions = ['.pdf', '.txt', '.md']
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    chunks = self.process_document(str(file_path))
                    all_chunks.extend(chunks)
                    print(f"Processed {file_path.name}: {len(chunks)} chunks")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    continue
        
        return all_chunks
    
    def get_chunking_strategy_info(self) -> Dict[str, Any]:
        """Return chunking configuration details."""
        return {
            'strategy': 'RecursiveCharacterTextSplitter',
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'separators': ["\\n\\n", "\\n", ". ", " ", ""]
        }

