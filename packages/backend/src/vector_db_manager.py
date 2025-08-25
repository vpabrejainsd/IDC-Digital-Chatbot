import os
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from config import CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL_NAME
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class VectorDBManager:
    """
    Manages vector storage and retrieval using ChromaDB.
    Handles document embeddings, similarity search, and context retrieval for RAG.
    """
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model."""
        self.client = PersistentClient(path=CHROMA_DB_PATH)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        self.collection = self._get_or_create_collection()
        # Initialize embedding model for similarity calculations
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def _get_or_create_collection(self):
        """Initialize ChromaDB collection for document storage."""
        try:
            collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            print(f"ChromaDB collection '{COLLECTION_NAME}' ready. Contains {collection.count()} documents.")
            return collection
        except Exception as e:
            print(f"Error initializing ChromaDB collection: {e}")
            return None

    def add_documents(self, embeddings: np.ndarray, chunks: List[Dict[str, Any]], force_reingestion: bool = True):
        """
        Add document chunks and their embeddings to ChromaDB collection.
        
        Args:
            embeddings: Numpy array of document embeddings
            chunks: List of text chunks with metadata
            force_reingestion: Whether to recreate collection if it exists
        """
        if not self.collection:
            print("ERROR: ChromaDB collection not initialized.")
            return

        # Check if we need to re-ingest documents
        existing_count = self.collection.count()
        if existing_count > 0:
            if not force_reingestion:
                print(f"Collection already contains {existing_count} documents. Use force_reingestion=True to recreate.")
                return
            else:
                print(f"Recreating collection (was {existing_count} documents)...")
                self.client.delete_collection(name=COLLECTION_NAME)
                self.collection = self.client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    embedding_function=self.embedding_function
                )

        # Prepare data for ChromaDB
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [{"source": chunk["source"]} for chunk in chunks]

        try:
            if ids:
                print(f"Adding {len(ids)} documents to ChromaDB...")
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"Successfully added {len(ids)} documents to ChromaDB.")
            else:
                print("No documents to add to ChromaDB.")
        except Exception as e:
            print(f"ERROR adding documents to ChromaDB: {e}")

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two embedding vectors."""
        vec1, vec2 = np.array(vec1), np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def keyword_match_score(self, query: str, doc_text: str) -> float:
        """
        Calculate keyword matching score between query and document text.
        Uses query term coverage with boosting for better matches.
        
        Args:
            query: User's search query
            doc_text: Document text content
            
        Returns:
            float: Keyword match score between 0.0 and 1.0
        """
        # Extract words from query and document (case-insensitive)
        query_words = set(re.findall(r'\w+', query.lower()))
        doc_words = set(re.findall(r'\w+', doc_text.lower()))
        
        if not query_words:
            return 0.0
        
        # Calculate how much of the query is covered by the document
        overlap = len(query_words & doc_words)
        query_coverage = overlap / len(query_words)
        
        # Boost score for better query coverage (max 1.0)
        return min(query_coverage * 1.5, 1.0)

    def retrieve_context(self, query: str, n_results: int = 5) -> List[str]:
        """
        Retrieve relevant document chunks from ChromaDB based on semantic and keyword similarity.
        
        Args:
            query: User's search query
            n_results: Maximum number of documents to retrieve
            
        Returns:
            List of formatted context strings containing source and content
        """
        if not self.collection:
            print("ERROR: ChromaDB collection not initialized.")
            return []

        try:
            print(f"\nSearching for: '{query}'")
            print("=" * 60)
            
            # Get semantic similarity results from ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            context = []
            if results and results['documents'] and results['documents'][0]:
                print(f"Found {len(results['documents'][0])} relevant documents:")
                print("-" * 40)
                
                # Get query embedding for cosine similarity calculation
                query_embedding = self.embedding_model.encode([query])[0]
                
                for i, doc_text in enumerate(results['documents'][0]):
                    source = results['metadatas'][0][i]['source']
                    
                    # Calculate semantic similarity
                    doc_embedding = self.embedding_model.encode([doc_text])[0]
                    cos_sim = self.cosine_similarity(query_embedding, doc_embedding)
                    
                    # Calculate keyword matching score
                    kw_score = self.keyword_match_score(query, doc_text)
                    
                    # Combine scores (semantic similarity weighted higher)
                    final_score = (0.7 * cos_sim) + (0.3 * kw_score)
                    
                    # Display scoring details
                    print(f"Document {i+1}:")
                    print(f"   Source: {os.path.basename(source)}")
                    print(f"   Semantic Score: {cos_sim:.4f}")
                    print(f"   Keyword Score: {kw_score:.4f}")
                    print(f"   Combined Score: {final_score:.4f}")
                    print(f"   Preview: {doc_text[:100]}...")
                    print("-" * 40)
                    
                    # Format context for LLM
                    context.append(f"Source: {source}\nContent: {doc_text}")
                
                # Display summary statistics
                cos_sims = [self.cosine_similarity(query_embedding, self.embedding_model.encode([doc])[0]) 
                           for doc in results['documents'][0]]
                kw_scores = [self.keyword_match_score(query, doc) for doc in results['documents'][0]]
                
                print(f"Summary Statistics:")
                print(f"   Avg Semantic Score: {np.mean(cos_sims):.4f}")
                print(f"   Avg Keyword Score: {np.mean(kw_scores):.4f}")
                print(f"   Best Match Score: {np.max(cos_sims):.4f}")
                print("=" * 60)
                
            else:
                print("No relevant documents found.")
                
            return context
            
        except Exception as e:
            print(f"ERROR retrieving context: {e}")
            return []