import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import requests
import mimetypes
import base64
import google.generativeai as genai
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import numpy as np
import chromadb
import uuid
from llama_parse import LlamaParse
import asyncio
import sys
import aiohttp

# Only apply nest_asyncio if we're not using uvloop
if 'uvloop' not in sys.modules:
    import nest_asyncio
    nest_asyncio.apply()

class RagAgent:
    def __init__(self):
        load_dotenv()
        self.llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        
        if not self.llama_api_key:
            raise ValueError("LLAMA_CLOUD_API_KEY not found in environment variables")
            
        # Initialize embedding model
        self.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder="./cache"
        )
        
        # Initialize Ollama endpoint
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.2"
        
        # Create data directory if it doesn't exist
        os.makedirs("./data/chroma", exist_ok=True)
        
        # Initialize ChromaDB with persistent storage
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma")
        
        # Initialize LlamaParse for document parsing
        self.parser = LlamaParse(
            api_key=self.llama_api_key,
            result_type="markdown"
        )
        
        # Initialize text splitter
        self.text_splitter = TokenTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Supported document types
        self.supported_mimes = {
            # Text Documents
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'text/plain': '.txt',
            'text/markdown': '.md',
            'application/rtf': '.rtf',
            
            # Presentations
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            
            # Spreadsheets
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'text/csv': '.csv',
            
            # Images
            'image/png': '.png',
            'image/jpeg': '.jpg',
            
            # Code
            'text/x-python': '.py',
            'application/javascript': '.js',
            'text/javascript': '.js'
        }

    def is_supported_file(self, file_content: bytes, filename: str) -> bool:
        """Check if the file type is supported."""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type in self.supported_mimes if mime_type else False

    async def process_document(self, file_content: bytes, filename: str, session_id: str) -> Dict:
        """
        Process a document through LlamaParse and prepare it for RAG.
        
        Args:
            file_content (bytes): The binary content of the file
            filename (str): Original filename with extension
            session_id (str): Unique session identifier
            
        Returns:
            Dict: Processed document data ready for RAG
        """
        try:
            # 1. Validate file type
            if not self.is_supported_file(file_content, filename):
                raise ValueError(f"Unsupported file type: {filename}")
            
            # 2. Parse document
            parsed_data = await self._parse_document(file_content, filename)
            
            # 3. Process for RAG
            processed_data = await self._prepare_for_rag(parsed_data)
            
            # 4. Store in ChromaDB
            await self._store_in_chroma(processed_data, session_id, filename)
            
            return {"status": "success", "message": "Document processed and stored successfully"}
                
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            raise

    async def _parse_document(self, file_content: bytes, filename: str) -> Dict:
        """Internal method to parse document using LlamaParse."""
        try:
            # Save temporary file
            temp_filename = f"temp_{filename}"
            with open(temp_filename, "wb") as f:
                f.write(file_content)
            
            # Parse document using LlamaParse with async method
            documents = await self.parser.aload_data(temp_filename)
            
            # Clean up temp file
            os.remove(temp_filename)
            
            if not documents:
                raise Exception("No content extracted from document")
                
            # Return the parsed content
            return {
                "content": documents[0].text,
                "metadata": documents[0].metadata
            }
                
        except Exception as e:
            print(f"Error parsing document: {str(e)}")
            raise

    async def _prepare_for_rag(self, parsed_data: Dict) -> Dict:
        """
        Prepare parsed document for RAG processing.
        - Takes LlamaParse output
        - Chunks the text while preserving context
        - Generates embeddings for chunks
        - Maintains metadata
        """
        try:
            # Extract text content from LlamaParse output
            content = parsed_data.get('content', '')
            metadata = parsed_data.get('metadata', {})
            
            # Create chunks using the text splitter
            chunks = self.text_splitter.split_text(content)
            
            # Generate embeddings for chunks
            embeddings = await self._generate_embeddings(chunks)
            
            # Prepare processed data
            processed_data = {
                'chunks': chunks,
                'embeddings': embeddings,
                'metadata': metadata,
                'total_chunks': len(chunks)
            }
            
            return processed_data
                
        except Exception as e:
            print(f"Error in _prepare_for_rag: {str(e)}")
            raise

    async def _generate_embeddings(self, chunks: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for text chunks using HuggingFace model.
        
        Args:
            chunks: List of text chunks to generate embeddings for
            
        Returns:
            List of numpy arrays containing embeddings
        """
        try:
            # Generate embeddings for all chunks
            embeddings = []
            for chunk in chunks:
                # Get embedding for single chunk
                embedding = self.embed_model.get_text_embedding(
                    text=chunk,
                )
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise

    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return list(set(self.supported_mimes.values()))

    async def _store_in_chroma(self, processed_data: Dict, session_id: str, filename: str):
        """Store processed document data in ChromaDB."""
        try:
            # Delete existing collection for this session if it exists
            try:
                self.chroma_client.delete_collection(name=f"session_{session_id}")
            except:
                pass  # Collection might not exist
            
            # Create new collection
            collection = self.chroma_client.create_collection(
                name=f"session_{session_id}",
                metadata={"filename": filename}
            )
            
            # Generate unique IDs for chunks
            chunk_ids = [str(uuid.uuid4()) for _ in processed_data['chunks']]
            
            # Prepare metadata for each chunk
            metadatas = [{
                "chunk_index": idx,
                "total_chunks": processed_data['total_chunks'],
                "source": filename,
                **processed_data['metadata']
            } for idx in range(len(processed_data['chunks']))]
            
            # Add data to collection
            collection.add(
                ids=chunk_ids,
                embeddings=processed_data['embeddings'],
                documents=processed_data['chunks'],
                metadatas=metadatas
            )
            
        except Exception as e:
            print(f"Error storing in ChromaDB: {str(e)}")
            raise

    async def get_relevant_context(self, query: str, session_id: str, n_results: int = 3) -> List[str]:
        """Get relevant document chunks for a query."""
        try:
            # Get collection for session
            collection = self.chroma_client.get_collection(name=f"session_{session_id}")
            
            # Generate embedding for query
            query_embedding = self.embed_model.get_text_embedding(query)
            
            # Query collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Return relevant chunks
            return results['documents'][0] if results['documents'] else []
            
        except Exception as e:
            print(f"Error getting relevant context: {str(e)}")
            raise

    async def answer_question(self, question: str, session_id: str) -> str:
        """
        Answer a question using RAG with local Llama 3.2 model.
        
        Args:
            question (str): User's question
            session_id (str): Session identifier
            
        Returns:
            str: Generated answer
        """
        try:
            # Get relevant context
            context_chunks = await self.get_relevant_context(question, session_id)
            
            if not context_chunks:
                return "I don't have enough context to answer that question. Please make sure a document is uploaded first."
            
            # Combine context chunks
            context = "\n\n".join(context_chunks)
            
            # Create prompt for Llama
            prompt = f'''Based on the following context, please answer the question. 
            If the answer cannot be found in the context, say so.
            
            Context:
            {context}
            
            Question: {question}
            '''
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            # Send request to Ollama
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "Sorry, I couldn't generate a response.")
                    else:
                        return f"Error: Received status code {response.status}"
            
        except Exception as e:
            print(f"Error answering question: {str(e)}")
            raise

    def edit_file(self, target_file: str, instructions: str, code_edit: str) -> None:
        """I will fix the string formatting in the answer_question method."""
        return {
            "target_file": "agents/rag_agent.py",
            "instructions": "I will fix the syntax error in the prompt string formatting",
            "code_edit": """
    async def answer_question(self, question: str, session_id: str) -> str:
        try:
            # Get relevant context
            context_chunks = await self.get_relevant_context(question, session_id)
            
            if not context_chunks:
                return "I don't have enough context to answer that question. Please make sure a document is uploaded first."
            
            # Combine context chunks
            context = "\n\n".join(context_chunks)
            
            # Create prompt for Llama
            prompt = f'''Based on the following context, please answer the question. 
            If the answer cannot be found in the context, say so.
            
            Context:
            {context}
            
            Question: {question}
            '''
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            # Send request to Ollama
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "Sorry, I couldn't generate a response.")
                    else:
                        return f"Error: Received status code {response.status}"
            
        except Exception as e:
            print(f"Error answering question: {str(e)}")
            raise
"""
        }
