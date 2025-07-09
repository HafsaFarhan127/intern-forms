import chromadb

# Create a singleton-like pattern
_client = None
_collection = None

def get_chroma_client():
    global _client
    if _client is None:
        _client =chromadb.PersistentClient(path="vectors.chroma")

    return _client

def get_collection(name='meow'):
    global _collection
    if _collection is None:
        client = get_chroma_client()
        print(name)

        try:
            _collection = client.get_collection(name=name)
            print('collection already exists')
        except:
            _collection = client.create_collection(name=name)
            print('collection dont exists')

    return _collection

def flatten_embeddings(embeddings):
    """
    Flatten embeddings to ensure they're in 2D format for ChromaDB.
    
    Args:
        embeddings: Can be 2D or 3D list of embeddings
    
    Returns:
        2D list of embeddings
    """
    if not embeddings:
        return []
    
    # If it's a 3D list like [[[...]]], flatten to 2D
    if isinstance(embeddings, list) and len(embeddings) == 1 and isinstance(embeddings[0], list):
        if isinstance(embeddings[0][0], list):
            return embeddings[0]  # Remove outer wrapper
    
    # If it's already 2D, return as is
    return embeddings


def gemini_to_chroma_embeddings(gemini_response):
    """
    Convert Gemini API embedding response to ChromaDB-compatible format.
    
    Args:
        gemini_response: EmbedContentResponse object from Gemini API
                        Contains embeddings=[ContentEmbedding(values=[...]), ...]
                        OR already processed list of embeddings
    
    Returns:
        List of lists of floats - format required by ChromaDB (2D list)
    """
    # Check if input is already a list of lists (processed embeddings)
    if isinstance(gemini_response, list):
        return flatten_embeddings(gemini_response)
    
    # Handle original Gemini API response format
    embeddings_list = []
    
    # Extract embeddings from the response
    for content_embedding in gemini_response.embeddings:
        # Each ContentEmbedding has a .values attribute with the actual embedding
        embedding_values = [float(value) for value in content_embedding.values]
        embeddings_list.append(embedding_values)
    
    return embeddings_list