import fitz  # PyMuPDF
from langchain.schema import Document as LCDocument
from dotenv import load_dotenv
from google import genai
from google.genai.types import EmbedContentConfig
from google.genai import types
from chromaDb import get_chroma_client, get_collection

import re
import os
from pathlib import Path 
import chromadb
from chromadb.utils import embedding_functions

# Loading the env file
load_dotenv()

chromaClient = get_chroma_client()
# chromaClient.delete_collection(name='trial')
collection = get_collection()  # in another module this is

dir = Path('c:/Users/hafsa/Documents/test_deep/my_forms')  # change this to the dir of project with pdf form folder
pdf_output = Path("c:/Users/hafsa/Documents/test_deep/converted_forms")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF"""
    doc = fitz.open(pdf_path)
    text_content = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_content += page.get_text()
        text_content += "\n\n"  # Add page breaks
    
    doc.close()
    return text_content

def extract_tables_from_pdf(pdf_path):
    """Extract tables from PDF using PyMuPDF"""
    doc = fitz.open(pdf_path)
    tables = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Find tables on the page
        page_tables = page.find_tables()
        
        for table in page_tables:
            try:
                # Extract table data
                table_data = table.extract()
                if table_data:
                    # Convert table to text format
                    table_text = ""
                    for row in table_data:
                        row_text = " | ".join([str(cell) if cell else "" for cell in row])
                        table_text += row_text + "\n"
                    
                    tables.append({
                        "text": table_text.strip(),
                        "page": page_num + 1
                    })
            except Exception as e:
                print(f"Error extracting table on page {page_num + 1}: {e}")
                continue
    
    doc.close()
    return tables

def extract_form_fields_from_pdf(pdf_path):
    """Extract form fields from PDF using PyMuPDF"""
    doc = fitz.open(pdf_path)
    form_fields = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Get form fields (widgets) on the page
        widgets = page.widgets()
        
        for widget in widgets:
            field_name = widget.field_name
            field_value = widget.field_value
            field_type = widget.field_type_string
            
            if field_name and field_value:
                form_fields.append({
                    "key": field_name,
                    "value": str(field_value),
                    "type": field_type,
                    "page": page_num + 1
                })
    
    doc.close()
    return form_fields

def chunk_text_by_sentences(text, max_chunk_size=500):
    """Split text into chunks by sentences"""
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def chunk_text_by_paragraphs(text, max_chunk_size=800):
    """Split text into chunks by paragraphs"""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        if len(current_chunk) + len(paragraph) < max_chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def pdfs_to_markdown(dir):
    """Convert PDFs to markdown using PyMuPDF"""
    for file in os.listdir(dir):
        if not file.lower().endswith('.pdf'):
            continue
            
        full_path = dir / file
        print(f"Processing: {full_path}")
        
        # Extract text content
        text_content = extract_text_from_pdf(str(full_path))
        
        # Extract tables
        tables = extract_tables_from_pdf(str(full_path))
        
        # Combine text and tables in markdown format
        markdown_output = "# " + file[:-4] + "\n\n"
        markdown_output += text_content
        
        if tables:
            markdown_output += "\n\n## Tables\n\n"
            for i, table in enumerate(tables):
                markdown_output += f"### Table {i+1} (Page {table['page']})\n\n"
                markdown_output += table['text'] + "\n\n"
        
        # Save to markdown file
        pdf_output.mkdir(parents=True, exist_ok=True)
        output_file_name = file[:-4] + ".md"
        output_file_path = pdf_output / output_file_name
        
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_output)
        print(f"Saved markdown to: {output_file_path}")

def gen_embeddings(chunk, client):
    """Generate embeddings for documents"""
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=chunk,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
        ),
    )
    return response

def gen_query_embeddings(chunk, client):
    """Generate embeddings for queries"""
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=chunk,
        config=types.EmbedContentConfig(
            task_type="SEMANTIC_SIMILARITY",
        ),
    )
    return response

def process_pdf_with_pymupdf(pdf_path, file_name):
    """Process a single PDF file and return chunks"""
    chunks = []
    
    try:
        # Extract form fields
        form_fields = extract_form_fields_from_pdf(pdf_path)
        for field in form_fields:
            with open("new_file.txt", "a") as file:
                file.write(field)
            chunks.append({
                "text": f"{field['key']}: {field['value']}",
                "metadata": {
                    "source": file_name,
                    "type": "field",
                    "field": field['key'],
                    "page": field['page']
                }
            })
        
        # Extract tables
        tables = extract_tables_from_pdf(pdf_path)
        for table in tables:
            if len(table['text']) > 20:
                with open("new_file.txt", "a") as file:
                    file.write(table['text'])
                chunks.append({
                    "text": table['text'],
                    "metadata": {
                        "source": file_name,
                        "type": "table",
                        "page": table['page']
                    }
                })
        
        # Extract and chunk text content
        text_content = extract_text_from_pdf(pdf_path)
        
        # Clean the text
        text_content = re.sub(r'\s+', ' ', text_content)  # Remove extra whitespace
        text_content = text_content.strip()
        
        # Split text into chunks
        text_chunks = chunk_text_by_paragraphs(text_content, max_chunk_size=800)
        
        for i, chunk_text in enumerate(text_chunks):
            if len(chunk_text) > 30:  # Only include substantial chunks
                with open("new_file.txt", "a") as file:
                    file.write(chunk_text)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "source": file_name,
                        "type": "text",
                        "chunk_id": i
                    }
                })
        
    except Exception as e:
        print(f"Error processing {file_name}: {e}")
    
    return chunks


# Main processing loop
all_chunks = []

for file in os.listdir(dir):
    if not file.lower().endswith('.pdf'):
        continue
        
    full_path = dir / file
    print(f"Processing: {full_path}")
    
    # Process PDF with PyMuPDF
    file_chunks = process_pdf_with_pymupdf(str(full_path), file)
    all_chunks.extend(file_chunks)
    
    print(f"Extracted {len(file_chunks)} chunks from {file}")

print(all_chunks)
print(f"Total chunks: {len(all_chunks)}")

# Generate embeddings and store in ChromaDB
if all_chunks:
    client = genai.Client()
    
    # Prepare texts for embedding
    texts_for_embedding = [chunk["text"] for chunk in all_chunks]
    
    # Generate embeddings
    embedded_content = gen_embeddings(texts_for_embedding, client)
    final_embed = [emb.values for emb in embedded_content.embeddings]
    
    print(f"First embedding dimension: {len(final_embed[0])}")
    
    # Add to ChromaDB
    collection.add(
        documents=texts_for_embedding,
        embeddings=final_embed,
        metadatas=[chunk["metadata"] for chunk in all_chunks],
        ids=[f"{chunk['metadata']['source']}_rec_{i}" for i, chunk in enumerate(all_chunks)]
    )
    
    print(f'Collection size: {collection.count()}')

# Query demo
query = input("Ask the magic carpet your question: ")
query_trans = gen_query_embeddings(query, client)
query_embed = [emb.values for emb in query_trans.embeddings]

# Flatten the query embedding
chroma_query = [item for sublist1 in query_embed for item in sublist1]

result = collection.query(query_embeddings=[chroma_query], n_results=5)
print("\nQuery Results:")
for i, (doc, metadata) in enumerate(zip(result['documents'][0], result['metadatas'][0])):
    print(f"\nResult {i+1}:")
    print(f"Source: {metadata['source']}")
    print(f"Type: {metadata['type']}")
    print(f"Content: {doc[:200]}...")
    print("-" * 50)