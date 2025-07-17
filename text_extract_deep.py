import fitz
import re
import os

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

def process_pdf_with_pymupdf(pdf_path, file_name):
    """Process a single PDF file and return chunks"""
    chunks = []
    
    try:
        # Extract form fields
        form_fields = extract_form_fields_from_pdf(pdf_path)
        
        for field in form_fields:
            print(field)
            with open("fields.txt", "a") as file:
                file.write(f"{field['key']}: {field['value']}\n")
        #     chunks.append({
        #         "text": f"{field['key']}: {field['value']}",
        #         "metadata": {
        #             "source": file_name,
        #             "type": "field",
        #             "field": field['key'],
        #             "page": field['page']
        #         }
        #     })
        
        # Extract tables
        # tables = extract_tables_from_pdf(pdf_path)
        # for table in tables:
        #     if len(table['text']) > 20:
        #         with open("new_file.txt", "a") as file:
        #             file.write(table['text'])
        #         chunks.append({
        #             "text": table['text'],
        #             "metadata": {
        #                 "source": file_name,
        #                 "type": "table",
        #                 "page": table['page']
        #             }
        #         })
        
        # Extract and chunk text content
        text_content = extract_text_from_pdf(pdf_path)
        # # Clean the text
        # text_content = re.sub(r'\s+', ' ', text_content)  # Remove extra whitespace
        # text_content = text_content.strip()
        with open(f"{file_name}.txt", "w") as file:
                    file.write(text_content)
        
        # # Clean the text
        # text_content = re.sub(r'\s+', ' ', text_content)  # Remove extra whitespace
        # text_content = text_content.strip()
        
        # # Split text into chunks
        # text_chunks = chunk_text_by_paragraphs(text_content, max_chunk_size=800)
        
        # for i, chunk_text in enumerate(text_chunks):
        #     if len(chunk_text) > 30:  # Only include substantial chunks
        #         with open("new_file.txt", "a") as file:
        #             file.write(chunk_text)
        #         chunks.append({
        #             "text": chunk_text,
        #             "metadata": {
        #                 "source": file_name,
        #                 "type": "text",
        #                 "chunk_id": i
        #             }
        #         })
        
    except Exception as e:
        print(f"Error processing {file_name}: {e}")
    
    print(f"Processed {file_name}")

for file in os.listdir(r"my_forms"):
    pdf_path = os.path.join(r"my_forms", file)
    process_pdf_with_pymupdf(pdf_path, file)