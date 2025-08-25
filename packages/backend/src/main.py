from config import DATA_FOLDER, GEMINI_API_KEY, IDC_CONTACT_EMAIL
from data_loader import load_documents_from_folder
from text_processor import chunk_text
from embedding_manager import EmbeddingManager
from vector_db_manager import VectorDBManager
from llm_manager import LLMManager
import os

# Initialize clean logging
try:
    from logging_config import setup_clean_logging
    setup_clean_logging()
except ImportError:
    pass  # Logging config not available

# Global RAG components
_embedding_manager = None
_vector_db_manager = None
_llm_manager = None

# Configuration flags
_SINGLE_FILE_TO_DEBUG = None
_FORCE_CHROMA_REINGESTION = True

def _init_rag_chatbot_components():
    """
    Initializes the RAG chatbot components using ChromaDB for vector storage.
    Loads JSON/JSONL documents, creates embeddings, and stores them in ChromaDB.
    """
    global _embedding_manager, _vector_db_manager, _llm_manager

    print("Initializing RAG Chatbot Components...")
    print("Processing JSON/JSONL files with ChromaDB vector storage")

    try:
        # Initialize core components
        print("Loading embedding model and LLM...")
        _embedding_manager = EmbeddingManager()
        _llm_manager = LLMManager()
        _vector_db_manager = VectorDBManager()

        # Validate component initialization
        model_valid = _embedding_manager.get_model() is not None
        llm_valid = _llm_manager.model is not None
        vector_valid = _vector_db_manager.collection is not None

        if not all([model_valid, vector_valid, llm_valid]):
            print("ERROR: Core RAG components failed to initialize:")
            print(f"   Embedding Manager: {'✅' if model_valid else '❌'}")
            print(f"   Vector Database: {'✅' if vector_valid else '❌'}")
            print(f"   LLM Manager: {'✅' if llm_valid else '❌'}")
            return

        # Load and process documents
        print("Loading documents from data folder...")
        documents = load_documents_from_folder(DATA_FOLDER, single_file_path=_SINGLE_FILE_TO_DEBUG)

        if not documents:
            print("WARNING: No documents found. Please add JSON/JSONL files to the data folder.")
            return

        print(f"Loaded {len(documents)} documents:")
        for doc in documents:
            print(f"   - {os.path.basename(doc['source'])}")

        # Create text chunks for vector storage
        print("Creating text chunks...")
        chunks = chunk_text(documents)
        if not chunks:
            print("ERROR: No text chunks created from documents.")
            return

        # Generate embeddings and store in ChromaDB
        print("Generating embeddings and storing in ChromaDB...")
        embeddings = _embedding_manager.create_embeddings(chunks)
        if embeddings is None:
            print("ERROR: Failed to create embeddings.")
            return

        _vector_db_manager.add_documents(embeddings, chunks, force_reingestion=_FORCE_CHROMA_REINGESTION)
        print(f"RAG system initialized successfully with {len(chunks)} chunks!")

    except Exception as e:
        print(f"ERROR during initialization: {e}")
        _embedding_manager = None
        _vector_db_manager = None
        _llm_manager = None


_init_rag_chatbot_components()

def ask_idc_chatbot(query: str) -> str:
    """
    Main function to process user queries using RAG (Retrieval-Augmented Generation).
    
    Args:
        query (str): User's question or query
        
    Returns:
        str: Generated response from the chatbot
    """
    # Check if components are properly initialized
    if not all([_vector_db_manager, _llm_manager]):
        error_msg = "Chatbot components not initialized. Please restart the system."
        print(f"ERROR: {error_msg}")
        return f"I'm sorry, {error_msg.lower()} For assistance, please contact IDC directly at {IDC_CONTACT_EMAIL}."

    try:
        # Retrieve relevant context from vector database
        print(f"Processing query: {query}")
        relevant_context = _vector_db_manager.retrieve_context(query, n_results=5)
        
        # Generate response using LLM with retrieved context
        response = _llm_manager.generate_response(query, relevant_context)
        return response
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(f"ERROR: {error_msg}")
        return f"I encountered a technical issue while processing your question. Please try again or contact IDC directly at {IDC_CONTACT_EMAIL} for assistance."

def main():
    """
    Console-based interactive chatbot for direct testing and usage.
    Allows users to ask questions in a command-line interface.
    """
    if not all([_vector_db_manager, _llm_manager]):
        print("ERROR: Chatbot components not properly initialized.")
        return

    print("\n" + "="*60)
    print("IDC CHATBOT - CONSOLE MODE")
    print("="*60)
    print("Type your questions below or 'exit' to quit")
    print("-"*60)

    while True:
        try:
            user_query = input("\nYour question: ").strip()
            
            if user_query.lower() in ['exit', 'quit', 'bye']:
                print("\nThank you for using IDC Chatbot. Goodbye!")
                break
                
            if not user_query:
                print("Please enter a question.")
                continue

            print("\nIDC Chatbot:")
            response = ask_idc_chatbot(user_query)
            print(response)
            print("-"*60)
            
        except KeyboardInterrupt:
            print("\n\nChatbot interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Please try again or type 'exit' to quit.")

def test_chatbot_queries():
    """
    Test the chatbot with common IDC-related queries to validate performance.
    Useful for debugging and performance monitoring.
    """
    test_queries = [
        "What cybersecurity services does IDC offer?",
        "Tell me about IDC's global presence",
        "How do I contact IDC technologies?",
        "What positions are available at IDC?",
        "What is IDC's experience with financial institutions?"
    ]
    
    print("\n" + "="*60)
    print("TESTING CHATBOT WITH SAMPLE QUERIES")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}] Query: {query}")
        print("-" * 50)
        try:
            response = ask_idc_chatbot(query)
            # Show first 150 characters of response
            preview = response[:150] + "..." if len(response) > 150 else response
            print(f"Response: {preview}")
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import sys
    
    # Initialize RAG components on startup
    _init_rag_chatbot_components()
    
    # Check command line arguments for different modes
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("Running chatbot tests...")
            test_chatbot_queries()
        elif sys.argv[1] == "console":
            main()
        else:
            print("Usage: python main.py [test|console]")
            print("  test    - Run test queries to validate chatbot performance")
            print("  console - Interactive console mode for chatbot")
            print("  (no args) - Default console mode")
    else:
        # Default behavior - run interactive console
        main()