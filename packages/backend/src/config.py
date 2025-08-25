import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  

# Get the backend directory (parent of src)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FOLDER = os.path.join(BACKEND_DIR, "data")

CHROMA_DB_PATH = os.path.join(BACKEND_DIR, "chroma_db")

COLLECTION_NAME = "company_data_collection"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

GEMINI_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    print(f"Created data folder: {DATA_FOLDER}")

if not os.path.exists(CHROMA_DB_PATH):
    os.makedirs(CHROMA_DB_PATH)
    print(f"Created ChromaDB folder: {CHROMA_DB_PATH}")

# In config.py, add JSON-specific configurations:

# File processing priority (JSON files first, then PPTX for image extraction)
FILE_PRIORITY = {
    '.json': 1,
    '.jsonl': 2,
    '.pptx': 3,  # Moved up priority for partner logo extraction
    '.pdf': 4,
    '.csv': 5,
    '.txt': 6  # Lowest priority
}

# JSON processing settings
JSON_PROCESSING = {
    'extract_metadata': True,
    'extract_images': True,
    'extract_notes': True,
    'extract_tables': True
}

# IDC Contact Information
IDC_CONTACT_EMAIL = "contact@idctechnologies.com"

# PPTX and OCR Processing Settings
PPTX_PROCESSING = {
    'extract_images': True,
    'extract_text': True,
    'use_ocr': True,
    'use_vlm': True,  # Use VLM for logo recognition
    'ocr_confidence_threshold': 0.6,
    'max_image_size': (1024, 1024),  # Resize large images for processing
    'supported_image_formats': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
}

# OCR Configuration
OCR_SETTINGS = {
    'tesseract_config': '--oem 3 --psm 6',  # OCR Engine Mode 3, Page Segmentation Mode 6
    'min_confidence': 60,
    'preprocess_images': True,
    'enhance_contrast': True,
    'remove_noise': True
}