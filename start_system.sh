#!/bin/bash

# PDF Chat System Startup Script
echo "🚀 Starting PDF Chat System..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install Node.js and npm first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create a .env file with your GEMINI_API_KEY."
    echo "Example:"
    echo "GEMINI_API_KEY=your_api_key_here"
    exit 1
fi

# Check if vector database exists
if [ ! -d "vectors.chroma" ]; then
    echo "⚠️  Vector database not found. Please run the PDF processing script first:"
    echo "python pymupdf.py  # or python chunking&embeddings(og).py"
    echo ""
    echo "Would you like to continue anyway? (y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        exit 1
    fi
fi

# Install Python dependencies if needed
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies if needed
echo "📦 Installing Node.js dependencies..."
cd pdf-chat-ui
npm install
cd ..

# Start the backend server in the background
echo "🐍 Starting Python Flask backend..."
python api_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start the frontend server
echo "⚛️  Starting React frontend..."
cd pdf-chat-ui
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo "✅ PDF Chat System is starting up!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $BACKEND_PID
wait $FRONTEND_PID