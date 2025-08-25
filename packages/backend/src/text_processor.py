from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP
from typing import List, Dict

def chunk_text(documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Split documents into smaller chunks for embedding and vector storage.
    Uses hierarchical text splitting to preserve document structure.
    
    Args:
        documents: List of documents with 'text' and 'source' fields
        
    Returns:
        List of text chunks with unique IDs, text content, and source information
    """
    
    # Define text splitting hierarchy (try these separators in order)
    separators = [
        "\n\n\n",  # Triple newlines (major sections)
        "\n\n",    # Double newlines (paragraphs)
        "\n",      # Single newlines (sentences)
        " ",       # Spaces (words)
        ""         # Character-level (last resort)
    ]

    # Initialize text splitter with configuration from config.py
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,           # Maximum chunk size (1000 chars)
        chunk_overlap=CHUNK_OVERLAP,     # Overlap between chunks (200 chars)
        length_function=len,             # Use character count
        is_separator_regex=False,        # Use literal string separators
        separators=separators            # Hierarchical splitting strategy
    )
    
    chunks = []
    chunk_id_counter = 0
    
    # Process each document
    for doc in documents:
        # Clean text by normalizing whitespace
        cleaned_text = " ".join(doc["text"].split()).strip()
        
        # Skip empty documents
        if not cleaned_text:
            print(f"Skipping empty document: {doc['source']}")
            continue

        # Split document into chunks
        doc_chunks = text_splitter.split_text(cleaned_text)
        
        # Create chunk objects with metadata
        for chunk_text in doc_chunks:
            chunks.append({
                "id": f"chunk_{chunk_id_counter}",  # Unique identifier
                "text": chunk_text,                   # Chunk content
                "source": doc["source"]              # Original source file
            })
            chunk_id_counter += 1
    
    print(f"Created {len(chunks)} text chunks from {len(documents)} documents.")
    return chunks
