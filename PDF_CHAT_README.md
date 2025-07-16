# PDF Document Chat System

A modern React + Vite frontend with Python Flask backend for chatting with PDF documents using AI embeddings and semantic search.

## Features

- **Modern Chat Interface**: Clean, responsive React UI with Tailwind CSS
- **PDF Processing**: Extract text, tables, and form fields from PDFs using PyMuPDF and Docling
- **AI-Powered Search**: Uses Google Gemini API for embeddings and semantic search
- **Vector Database**: ChromaDB for efficient similarity search
- **Real-time Chat**: Interactive chat interface with typing indicators
- **Source Attribution**: Shows which document and page information comes from
- **Error Handling**: Graceful fallbacks and error messages

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Flask API      │    │  PDF Processing │
│   (Vite + React)│◄──►│  (Python)       │◄──►│  (ChromaDB)     │
│   - Chat UI     │    │  - Query API    │    │  - Embeddings   │
│   - Tailwind    │    │  - CORS enabled │    │  - Semantic     │
│   - Components  │    │  - Error handle │    │    Search       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Google Gemini API key

### 1. Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

3. **Process your PDF documents:**
Before running the chat system, you need to process your PDF documents. Update the directory paths in your PDF processing scripts (`chunking&embeddings(og).py` or `pymupdf.py`):

```python
# Update these paths to point to your PDF documents
dir = Path('your/pdf/documents/directory')
pdf_output = Path("your/output/directory")
```

Then run the processing script:
```bash
python pymupdf.py  # or chunking&embeddings(og).py
```

4. **Start the Flask API server:**
```bash
python api_server.py
```

The API will be available at `http://localhost:5000`

### 2. Frontend Setup

1. **Navigate to the frontend directory:**
```bash
cd pdf-chat-ui
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. **Start both servers:**
   - Backend: `python api_server.py`
   - Frontend: `cd pdf-chat-ui && npm run dev`

2. **Open your browser** and navigate to `http://localhost:5173`

3. **Chat with your documents:**
   - Use the sample questions for quick access
   - Type your own questions about the PDF content
   - View responses with source attribution
   - See which document, page, and content type each answer comes from

## API Endpoints

### `/api/health` (GET)
Health check endpoint that returns system status.

### `/api/query` (POST)
Query the PDF documents using semantic search.

**Request body:**
```json
{
  "query": "What forms do I need to fill out?",
  "n_results": 5
}
```

**Response:**
```json
{
  "query": "What forms do I need to fill out?",
  "results": [
    {
      "content": "Form W-4 is required for all new employees...",
      "metadata": {
        "source": "Employee_Handbook.pdf",
        "type": "text",
        "page": 5
      },
      "relevance_score": 0.85
    }
  ],
  "total_results": 3,
  "processing_time": 1.2
}
```

### `/api/documents` (GET)
Get list of available processed documents.

### `/api/collection/stats` (GET)
Get statistics about the document collection.

## File Structure

```
├── api_server.py              # Flask API server
├── chromaDb.py               # ChromaDB utilities
├── chunking&embeddings(og).py # PDF processing with Docling
├── pymupdf.py                # PDF processing with PyMuPDF
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── pdf-chat-ui/             # React frontend
    ├── src/
    │   ├── components/
    │   │   ├── Message.jsx
    │   │   ├── MessageInput.jsx
    │   │   └── TypingIndicator.jsx
    │   ├── services/
    │   │   └── pdfApi.js
    │   ├── App.jsx
    │   └── index.css
    ├── package.json
    └── tailwind.config.js
```

## Configuration

### Frontend Configuration
Update the API base URL in `pdf-chat-ui/src/services/pdfApi.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Backend Configuration
Update document paths in your PDF processing scripts:
```python
dir = Path('path/to/your/pdf/documents')
pdf_output = Path("path/to/output/directory")
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure Flask-CORS is installed and the API server is running
2. **API Connection Failed**: Check if the Flask server is running on port 5000
3. **No Documents Found**: Ensure you've processed your PDF documents first
4. **Embedding Errors**: Verify your Google Gemini API key is set correctly

### Logs

- **Backend logs**: Check the Flask server console for API errors
- **Frontend logs**: Check browser console for client-side errors

## Development

### Adding New Features

1. **New API Endpoints**: Add routes to `api_server.py`
2. **New Components**: Create components in `pdf-chat-ui/src/components/`
3. **Styling**: Use Tailwind CSS classes for consistent styling

### Building for Production

```bash
cd pdf-chat-ui
npm run build
```

This creates a `dist` folder with production-ready files.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational/development purposes. Make sure to comply with the licenses of all dependencies.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are properly installed
4. Verify your API keys and environment variables