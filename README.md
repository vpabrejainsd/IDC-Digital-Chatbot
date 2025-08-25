# IDC Chatbot - Enterprise RAG System

A production-ready Retrieval-Augmented Generation (RAG) chatbot built with Python Flask backend and React TypeScript frontend, powered by Google Gemini LLM and ChromaDB vector storage.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Backend Setup
```bash
cd packages/backend
cp .env.example .env
# Add your GEMINI_API_KEY to .env
pip install -r requirements.txt
flask run
```

### Frontend Setup
```bash
cd packages/frontend
cp .env.example .env
# Set VITE_FLASK_BACKEND_URL=http://localhost:5000
npm install
npm run dev
```

## 📋 Architecture Overview

**Tech Stack:**
- **Backend**: Python Flask, ChromaDB, SQLite, Google Gemini LLM
- **Frontend**: React 19, TypeScript, TailwindCSS v4, Vite
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2

**Data Flow:**
```
Documents → Text Chunking → Embeddings → ChromaDB → Similarity Search → Gemini LLM → Response
```

**Supported Formats**: JSON/JSONL (priority), PDF, PPTX, CSV, TXT, Images (OCR)

## 🏗️ Project Structure

```
packages/
├── backend/          # Python Flask API with RAG pipeline
│   ├── src/         # Source code
│   ├── data/        # Document storage
│   ├── tests/       # Test suite
│   └── requirements.txt
└── frontend/        # React TypeScript UI
    ├── src/         # Source code
    ├── public/      # Static assets
    └── package.json
```

## 📚 Key Features

- **Intelligent Document Processing**: Automatic text extraction and chunking
- **Vector Search**: Semantic similarity matching with ChromaDB
- **Conversational Memory**: Context-aware multi-turn conversations
- **User Management**: Registration and session tracking
- **Multi-format Support**: PDF, PPTX, CSV, TXT, Images with OCR

## 🔧 Configuration

### Backend Configuration (config.py)
- **Gemini Model**: gemini-2.5-flash-lite-preview-06-17
- **Chunk Size**: 1000 characters with 200 overlap
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2

### API Endpoints
- `POST /register` - User registration
- `POST /chat` - Chat with the bot
- `GET /health` - Health check

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd packages/backend
python -m pytest tests/

# Frontend tests
cd packages/frontend
npm test
```

### Code Quality
```bash
# Backend linting
cd packages/backend
flake8 src/
black src/
mypy src/

# Frontend linting
cd packages/frontend
npm run lint
npm run type-check
```

## 📖 Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [API Documentation](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Developer Guide](docs/development/getting-started.md)

## 🚀 Recent Updates

### Phase 1 Completed ✅
- Fixed RAG pipeline JSON/JSONL extraction
- Implemented proper database initialization
- Added comprehensive error handling
- API endpoint standardization

### Phase 2 Roadmap 🎯
- Comprehensive testing suite
- Enhanced security measures
- Performance optimization
- Code architecture improvements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request