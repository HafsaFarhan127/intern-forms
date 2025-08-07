import re
import os
from pathlib import Path 
from langchain.schema import Document as LCDocument
from dotenv import load_dotenv
from chromaDb import get_chroma_client, get_collection
from llm_calls import gen_embeddings, gen_query_embeddings

# Loading the env file
load_dotenv()
collection = get_collection()  

dir = Path('C:\\Users\\t822531\\UBS\\Dev\\RAG\\duck_pdf_to_txt')  # change this to the dir of project with txt file folder
txt_output = Path("C:\\Users\\t822531\\UBS\\Dev\\RAG\\my_forms")

def extract_text_from_txt(txt_path):
    """Extract text from TXT file"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
        return text_content
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            with open(txt_path, 'r', encoding='latin-1') as file:
                text_content = file.read()
            return text_content
        except Exception as e:
            print(f"Error reading file {txt_path}: {e}")
            return ""

def clean_text(text):
    """Clean text by removing whitespaces, <!-- image--> tags, and special characters"""
    # Remove <!-- image--> tags (case insensitive)
    text = re.sub(r'<!--\s*image\s*-->', '', text, flags=re.IGNORECASE)
    
    # Remove other HTML-like comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Remove excessive whitespace (multiple spaces, tabs, newlines)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    # This keeps letters, numbers, basic punctuation, and spaces
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]', '', text)
    
    # Remove extra spaces around punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)
    
    # Clean up multiple consecutive punctuation marks
    text = re.sub(r'([.,!?;:]){2,}', r'\1', text)

    #Clean text by removing the '------'
    text=re.sub(r'^-','',text,flags=re.MULTILINE)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    print(text)
    return text


def estimate_tokens(text):
    """Estimate token count for text (rough approximation: 1 token ≈ 4 characters)"""
    return len(text) // 4

def chunk_text_by_sentences(text, max_tokens=7000):
    """Split text into chunks by sentences with token limit"""
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        test_chunk = current_chunk + sentence + ". "
        if estimate_tokens(test_chunk) < max_tokens:
            current_chunk = test_chunk
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def chunk_text_by_paragraphs(text, max_tokens=7000):
    """Split text into chunks by paragraphs with token limit"""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        test_chunk = current_chunk + paragraph + "\n\n"
        if estimate_tokens(test_chunk) < max_tokens:
            current_chunk = test_chunk
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def chunk_text_intelligently(text, max_tokens=7000):
    """Intelligent chunking that tries paragraphs first, then sentences if needed"""
    # First try paragraph-based chunking
    para_chunks = chunk_text_by_paragraphs(text, max_tokens)
    
    final_chunks = []
    for chunk in para_chunks:
        # If a paragraph chunk is still too large, split it by sentences
        if estimate_tokens(chunk) > max_tokens:
            sentence_chunks = chunk_text_by_sentences(chunk, max_tokens)
            final_chunks.extend(sentence_chunks)
        else:
            final_chunks.append(chunk)
    
    return final_chunks

def process_txt_file(txt_path, file_name):
    """Process a single TXT file and return chunks"""
    chunks = []
    
    try:
        # Extract text content
        text_content = extract_text_from_txt(txt_path)
        
        if not text_content:
            print(f"No content found in {file_name}")
            return chunks
        
        # Clean the text
        cleaned_text = clean_text(text_content)
        
        # Save cleaned text to a file for inspection
        cleaned_file_name = f'{file_name}_cleaned.txt'
        # with open(cleaned_file_name, 'w', encoding="utf-8") as file:
        #     file.write(cleaned_text)
        
        # Split text into chunks with token limit
        text_chunks = chunk_text_intelligently(cleaned_text, max_tokens=7000)
        
        for i, chunk_text in enumerate(text_chunks):
            if len(chunk_text) > 30:  # Only include substantial chunks
                token_count = estimate_tokens(chunk_text)
                print(len(chunk_text),'chunks is:',chunk_text)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "source": file_name,
                        "type": "text",
                        "chunk_id": i,
                        "estimated_tokens": token_count
                    }
                })
        
    except Exception as e:
        print(f"Error processing {file_name}: {e}")
    
    return chunks

# Main processing loop
all_chunks = []

for file in os.listdir(dir):
    # Process only .txt files
    # if not file.lower().endswith('.txt'):
    #     continue
        
    full_path = dir / file
    print(f"Processing: {full_path}")
    
    # Process TXT file
    file_chunks = process_txt_file(str(full_path), file)
    all_chunks.extend(file_chunks)
    
    print(f"Extracted {len(file_chunks)} chunks from {file}")

print(f"Total chunks: {len(all_chunks)}")

# Generate embeddings and store in ChromaDB
if all_chunks:
    
    # Prepare texts for embedding
    texts_for_embedding = [chunk["text"] for chunk in all_chunks]
    print(f'Texts for embedding: {len(texts_for_embedding)}')
    
    # Generate embeddings
    embedded_content = gen_embeddings(texts_for_embedding)
    
    # Add to ChromaDB
    collection.add(
        documents=texts_for_embedding,
        embeddings=embedded_content,
        metadatas=[chunk["metadata"] for chunk in all_chunks],
        ids=[f"{chunk['metadata']['source']}_rec_{i}" for i, chunk in enumerate(all_chunks)]
    )
    
    print(f'Collection size: {collection.count()}')

# Query demo
query = input("Ask the magic carpet your question: ")
query_embed = gen_query_embeddings(query)
print('this is query:', len(query_embed))

# This will query chromDB through comparison of query embeddings and document embeddings.
result = collection.query(query_embeddings=[query_embed], n_results=5)
print("\nQuery Results:")
for i, (doc, metadata) in enumerate(zip(result['documents'][0], result['metadatas'][0])):
    print(f"\nResult {i+1}:")
    print(f"Source: {metadata['source']}")
    print(f"Type: {metadata['type']}")
    print(f"Content: {doc[:200]}...")
    print("-" * 50)