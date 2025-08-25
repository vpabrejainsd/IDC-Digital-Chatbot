from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME
import numpy as np
from typing import List, Dict, Optional

class EmbeddingManager:
    """
    Manages text embedding generation using SentenceTransformers.
    Converts text chunks into dense vector representations for semantic search.
    """
    
    def __init__(self):
        """Initialize embedding manager and load the model."""
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the SentenceTransformer model for creating embeddings."""
        try:
            print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            print("Please ensure you have internet connection or the model is cached locally.")
            self.model = None

    def get_model(self) -> Optional[SentenceTransformer]:
        """Get the loaded SentenceTransformer model."""
        return self.model

    def create_embeddings(self, chunks: List[Dict[str, str]]) -> Optional[np.ndarray]:
        """
        Generate dense vector embeddings for text chunks.
        
        Args:
            chunks: List of text chunks with 'text' field
            
        Returns:
            numpy array of embeddings or None if model not loaded
        """
        if not self.model:
            print("Embedding model not loaded. Cannot create embeddings.")
            return None

        # Extract text content from chunks
        texts = [chunk["text"] for chunk in chunks]
        
        if not texts:
            print("No text content found in chunks.")
            return None
        
        try:
            print(f"Generating embeddings for {len(texts)} chunks...")
            # Create embeddings with progress bar
            embeddings = self.model.encode(
                texts, 
                show_progress_bar=True,
                batch_size=32,  # Process in batches for efficiency
                normalize_embeddings=True  # Normalize for better similarity search
            )
            print(f"Generated {len(embeddings)} embeddings.")
            return embeddings
            
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return None
