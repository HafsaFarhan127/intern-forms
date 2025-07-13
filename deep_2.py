from docling.document_converter import DocumentConverter
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

#loading the env file
load_dotenv()

chromaClient=get_chroma_client()
#chromaClient.delete_collection(name='trial')
collection=get_collection() #in another module this is

dir = Path('c:/Users/hafsa/Documents/test_deep/my_forms')  #change this to the dir of project with pdf form folder
pdf_output=Path("c:/Users/hafsa/Documents/test_deep/converted_forms")
#print(pdf_output)

#function to iterate files in folder to auto-convert pdfs to rag compatible formats
def pdfsTomark(dir):
    for file in os.listdir(dir):
        full_path=f'{dir}\\{file}' #change this to dir/file as its a PATH obj
        source = full_path  # document per local path or URL
        print(source)
        converter = DocumentConverter()
        result = converter.convert(source)
        markdown_output=result.document.export_to_markdown()
        print('-'*80)

        pdf_output.mkdir(parents=True, exist_ok=True) # Ensure output directory exists

        output_file_name = file[:-4] + ".md"
        output_file_path = pdf_output / output_file_name
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_output)
        print(f" Saved markdown to: {output_file_path}")

   #function for embedding tweaks here to compare different versions
def gen_Embeddings(chunk,client):

    response = client.models.embed_content(
    model="text-embedding-004",
    contents=chunk,
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",  # Optional
        # output_dimensionality=3072,  # Optional
        # title="Driver's License",  # Optional
    ),
)
    return response

def gen_QueryEmbeddings(chunk,client):

    response = client.models.embed_content(
    model="text-embedding-004",
    contents=chunk,
    config=types.EmbedContentConfig(
        task_type="SEMANTIC_SIMILARITY",  # changed this to search for similarity cuz query
        # output_dimensionality=3072,  # Optional
        # title="Driver's License",  # Optional
    ),
)
    return response



#function for chunking
#chunks = []
chunks = [] #for now this will be here to do 1-by-1 processing but shift this to out-of-loop for batch processing

for file in os.listdir(dir):
    full_path=f'{dir}\\{file}'
    source = full_path  # document per local path or URL
    print(source)
    converter = DocumentConverter()
    result = converter.convert(source)
    doc = result.document

    
    # Key-value fields
    for kv in doc.key_value_items:
        key = kv.key.strip()
        value = kv.value.strip()
        if key and value:
            chunks.append({
                "text": f"{key}: {value}",
                "metadata": {
                    "source": file,
                    "type": "field",
                    "field": key
                }
            })

    # Tables
    for tbl in doc.tables:
        tbl_text = tbl.to_text().strip()
        if len(tbl_text) > 20:
            chunks.append({
                "text": tbl_text,
                "metadata": {
                    "source": file,
                    "type": "table"
                }
            })

    # Descriptive text
    for txt in doc.texts:
        content = txt.text.strip()
        if len(content) > 30:
            chunks.append({
                "text": content,
                "metadata": {
                    "source": file,
                    "type": "text"
                }
            })

    print(chunks)
    print(len(chunks))
    # Save all chunks to a txt file (append mode, so it does not get overwritten)

print(chunks)
with open("chunks_output.txt", "a", encoding="utf-8") as f:
    for chunk in chunks:
        f.write(chunk["text"] + "\n")


