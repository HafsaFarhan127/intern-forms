from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
import logging
import traceback
from google import genai
from google.genai import types
from chromaDb import get_chroma_client, get_collection
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the PDF processing system
try:
    chroma_client = get_chroma_client()
    collection = get_collection()
    gemini_client = genai.Client()
    logger.info("PDF processing system initialized successfully")
except Exception as e:
    logger.error(f"Error initializing PDF processing system: {e}")
    chroma_client = None
    collection = None
    gemini_client = None

def gen_query_embeddings(query, client):
    """Generate embeddings for queries using Gemini API"""
    try:
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=query,
            config=types.EmbedContentConfig(
                task_type="SEMANTIC_SIMILARITY",
            ),
        )
        return response
    except Exception as e:
        logger.error(f"Error generating query embeddings: {e}")
        raise

def format_chat_response(results, query):
    """Format ChromaDB results into a chat-friendly response"""
    if not results or not results.get('documents') or not results['documents'][0]:
        return {
            "query": query,
            "results": [],
            "total_results": 0,
            "message": "No relevant information found in the documents."
        }
    
    documents = results['documents'][0]
    metadatas = results.get('metadatas', [None])[0] if results.get('metadatas') else [None] * len(documents)
    distances = results.get('distances', [None])[0] if results.get('distances') else [None] * len(documents)
    
    formatted_results = []
    for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
        result = {
            "content": doc,
            "metadata": metadata or {},
            "relevance_score": 1 - distance if distance is not None else 0.5
        }
        formatted_results.append(result)
    
    return {
        "query": query,
        "results": formatted_results,
        "total_results": len(formatted_results),
        "message": f"Found {len(formatted_results)} relevant results."
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "chroma_initialized": collection is not None,
        "gemini_initialized": gemini_client is not None,
        "collection_count": collection.count() if collection else 0
    })

@app.route('/api/query', methods=['POST'])
def query_documents():
    """Query the PDF documents using semantic search"""
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        
        logger.info(f"Processing query: {query}")
        
        # Check if system is initialized
        if not collection or not gemini_client:
            return jsonify({"error": "PDF processing system not initialized"}), 500
        
        # Generate query embeddings
        query_embeddings = gen_query_embeddings(query, gemini_client)
        query_embed = [emb.values for emb in query_embeddings.embeddings]
        
        # Flatten the query embedding
        chroma_query = [item for sublist in query_embed for item in sublist]
        
        # Search in ChromaDB
        results = collection.query(
            query_embeddings=[chroma_query],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format response
        response = format_chat_response(results, query)
        response['processing_time'] = time.time() - start_time
        
        logger.info(f"Query processed successfully in {response['processing_time']:.2f} seconds")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of available documents"""
    try:
        # Get unique sources from the collection
        if not collection:
            return jsonify({"error": "Collection not initialized"}), 500
        
        # Get all documents to extract unique sources
        all_results = collection.get(include=['metadatas'])
        
        if not all_results or not all_results.get('metadatas'):
            return jsonify({"documents": []})
        
        # Extract unique sources
        sources = set()
        for metadata in all_results['metadatas']:
            if metadata and 'source' in metadata:
                sources.add(metadata['source'])
        
        # Format as document list
        documents = []
        for i, source in enumerate(sorted(sources)):
            documents.append({
                "id": i + 1,
                "name": source,
                "status": "processed",
                "chunks": len([m for m in all_results['metadatas'] if m and m.get('source') == source])
            })
        
        return jsonify({"documents": documents})
        
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/collection/stats', methods=['GET'])
def get_collection_stats():
    """Get statistics about the current collection"""
    try:
        if not collection:
            return jsonify({"error": "Collection not initialized"}), 500
        
        count = collection.count()
        
        # Get sample of metadata to understand data structure
        sample = collection.get(limit=10, include=['metadatas'])
        
        # Analyze metadata
        types_count = {}
        sources_count = {}
        
        if sample and sample.get('metadatas'):
            for metadata in sample['metadatas']:
                if metadata:
                    doc_type = metadata.get('type', 'unknown')
                    source = metadata.get('source', 'unknown')
                    
                    types_count[doc_type] = types_count.get(doc_type, 0) + 1
                    sources_count[source] = sources_count.get(source, 0) + 1
        
        return jsonify({
            "total_chunks": count,
            "types_distribution": types_count,
            "sources_distribution": sources_count,
            "sample_size": len(sample['metadatas']) if sample and sample.get('metadatas') else 0
        })
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/process', methods=['POST'])
def process_new_documents():
    """Trigger processing of new documents (placeholder)"""
    try:
        # This endpoint can be used to trigger reprocessing of documents
        # For now, it just returns the current collection count
        if not collection:
            return jsonify({"error": "Collection not initialized"}), 500
        
        count = collection.count()
        return jsonify({
            "message": "Processing would be triggered here",
            "current_collection_size": count
        })
        
    except Exception as e:
        logger.error(f"Error in process endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Check if required environment variables are set
    required_env_vars = ['GEMINI_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these in your .env file")
    else:
        logger.info("Starting PDF Chat API server...")
        logger.info(f"Collection initialized: {collection is not None}")
        logger.info(f"Gemini client initialized: {gemini_client is not None}")
        
        if collection:
            logger.info(f"Collection contains {collection.count()} chunks")
        
        app.run(debug=True, host='0.0.0.0', port=5000)