from docling.document_converter import DocumentConverter
from langchain.schema import Document as LCDocument
from dotenv import load_dotenv
from google import genai

from google.genai.types import EmbedContentConfig
from google.genai import embed_content

import re
import os
from pathlib import Path 

#loading the env file
load_dotenv()

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

#function for chunking
#chunks = []
for file in os.listdir(dir):
    '''
    full_path=f'{dir}\\{file}'
    source = full_path  # document per local path or URL
    print(source)
    converter = DocumentConverter()
    result = converter.convert(source)
    doc = result.document
    '''

    # chunks = [] #for now this will be here to do 1-by-1 processing but shift this to out-of-loop for batch processing
    chunks = [{'text': 'Vested Benefits Foundation of UBS AG P.O. Box CH-8098 Zurich', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Authorisation to give information', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Details of pension account holder¹', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'AHV number / Social security number (756.xxxx.xxxx.xx)', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'The authorised representative (only individual persons) is hereby permitted to obtain information regarding the UBS vested benefits account and the UBS vested benefits custody account from the Vested Benefits Foundation of UBS AG ("Vested Benefits Foundation") on behalf of the pension account holder.', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': "The pension account holder is aware that the Vested Benefits Foundation exercises no control whatsoever over the actions of the authorised representative that they chooses. Therefore, it shall be the authorised representative's exclusive responsibility to notify the pension account holder of their actions.", 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': "This authorisation shall remain valid until it is expressly revoked by written communication sent to the Vested Benefits Foundation. This authorisation shall remain in force without restriction even in the event of incapacity of the pension account holder. Once the Vested Benefits Foundation has knowledge of the pension account holder's death, this authorisation shall be considered void as of the date on which the information has been received.", 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'The present authorisation shall be exclusively governed by and construed in accordance with Swiss law.', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': "The place of performance of all obligations of both parties as well as the exclusive place of jurisdiction for any disputes arising out of and in connection with the present authorisation is the Swiss foundation's seat.", 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'The Vested Benefits Foundation is empowered, however, to assert its rights as well before any other competent authority, in which event exclusively Swiss law shall remain applicable.', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': '67299  E V0 001 BAUK 19.01.2024 BDB N1', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Vested Benefits Foundation of UBS AG P.O. Box, CH-8098 Zurich Tel.+41-61-226 75 75', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Vested Benefits Foundation of UBS AG', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Send original to the Vested Benefits Foundation of UBS AG.', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Signature of the authorised representative (Please enclose a copy of signed identity document)', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Name of the authorised representative', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Signature of the pension account holder (Please enclose a copy of signed identity document)', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Name of the pension account holder', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': '¹ The singular form also includes the plural, and all masculine terms referring to persons refer to persons of both genders.', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}, {'text': 'Signature(s) verified / Signed in my presence', 'metadata': {'source': 'authorisation-to-inform-en.pdf', 'type': 'text'}}]


    '''
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
    '''
    #THIS IS THE START OF EMBEDDING TRIALS USING GEMINI FREE API 
        
    # The client gets the API key from the environment variable `GEMINI_API_KEY`.(built-in if i have another api name then need to pass it in as param)
    client = genai.Client() #request to llm
    texts_for_embedding = [chunk["text"] for chunk in chunks] #this got created because the embedding isnt working now for the other types other than text only

    embedded_content = client.models.embed_content(
    model="text-embedding-004",
    contents=texts_for_embedding,
    config=EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",  # Optional
        output_dimensionality=3072,  # Optional
        title="Driver's License",  # Optional
    ),
)
    final_embed=[emb.values for emb in embedded_content.embeddings]
    print(final_embed[0])
        

