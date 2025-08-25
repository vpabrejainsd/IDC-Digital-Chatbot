# Backend - Internship Chatbot

This is the backend service for the Internship Chatbot, providing AI-powered responses and data management.

## Architecture

The backend follows a modular architecture:

- **Data Loader**: Handles document ingestion from various formats (PDF, PPTX, CSV, TXT, Images)
- **Text Processor**: Chunks and prepares text for embedding
- **Embedding Manager**: Creates vector embeddings using Sentence Transformers
- **Vector DB Manager**: Manages ChromaDB for vector storage and retrieval
- **LLM Manager**: Handles Gemini API integration for response generation
- **Flask API**: Provides REST endpoints for the frontend

## Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Copy `.env.example` to `.env` and update with your API keys:
   ```bash
   cp .env.example .env
   ```

4. **Initialize Database**:
   ```bash
   python src/db.py
   ```

5. **Add Data Files**:
   Place your document files in the `data/` directory.

## Running the Server

```bash
cd src
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

- `GET /` - Health check
- `POST /register` - Register a new user
  - Body: `{"name": "string", "email": "string"}`
- `POST /ask` - Ask the chatbot a question
  - Body: `{"email": "string", "query": "string"}`

## Development

To run in development mode:
```bash
export FLASK_ENV=development
python src/app.py
```

## Testing

Run tests with:
```bash
pytest tests/
```

## Dependencies

- **Tesseract OCR**: Required for image text extraction
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt-get install tesseract-ocr`
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
