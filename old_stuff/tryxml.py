import fitz  # PyMuPDF
import xml.etree.ElementTree as ET
import json
import os
from pathlib import Path
import pikepdf
from bs4 import BeautifulSoup
import zipfile
import tempfile

class XFAExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.extracted_data = {}
        
    def extract_with_pymupdf(self):
        """
        Method 1: Extract XFA data using PyMuPDF
        This is the most reliable method for most XFA forms
        """
        print("🔍 Attempting extraction with PyMuPDF...")
        
        try:
            # Open PDF document
            doc = fitz.open(self.pdf_path)
            
            # Get XFA data if available
            xfa_data = doc.xfa_data()
            
            if xfa_data:
                print("✅ XFA data found!")
                
                # Parse XML data
                try:
                    root = ET.fromstring(xfa_data)
                    self.extracted_data['xfa_xml'] = self._parse_xml_data(root)
                    print(f"📊 Extracted {len(self.extracted_data['xfa_xml'])} XFA fields")
                except ET.ParseError as e:
                    print(f"❌ XML parsing error: {e}")
                    # Store raw data as fallback
                    self.extracted_data['xfa_raw'] = xfa_data
            else:
                print("⚠️ No XFA data found in document")
                
            # Try to get form fields as fallback
            form_fields = self._extract_form_fields(doc)
            if form_fields:
                self.extracted_data['form_fields'] = form_fields
                print(f"📋 Extracted {len(form_fields)} form fields")
                
            doc.close()
            return self.extracted_data
            
        except Exception as e:
            print(f"❌ PyMuPDF extraction failed: {e}")
            return None
    
    def extract_with_pikepdf(self):
        """
        Method 2: Extract XFA data using pikepdf (low-level approach)
        This method works for complex XFA structures
        """
        print("🔍 Attempting extraction with pikepdf...")
        
        try:
            # Open PDF with pikepdf
            with pikepdf.open(self.pdf_path) as pdf:
                
                # Look for XFA objects
                if '/AcroForm' in pdf.Root:
                    acro_form = pdf.Root['/AcroForm']
                    
                    if '/XFA' in acro_form:
                        xfa_obj = acro_form['/XFA']
                        print("✅ XFA object found!")
                        
                        # XFA can be an array or stream
                        if isinstance(xfa_obj, pikepdf.Array):
                            # Extract XFA streams from array
                            xfa_data = self._extract_xfa_from_array(xfa_obj)
                        else:
                            # Single XFA stream
                            xfa_data = bytes(xfa_obj)
                            
                        # Parse extracted data
                        if xfa_data:
                            parsed_data = self._parse_xfa_data(xfa_data)
                            self.extracted_data['pikepdf_xfa'] = parsed_data
                            print(f"📊 Extracted XFA data with pikepdf")
                        
                return self.extracted_data
                
        except Exception as e:
            print(f"❌ pikepdf extraction failed: {e}")
            return None
    
    def _extract_form_fields(self, doc):
        """Extract regular form fields from PDF"""
        fields = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get form fields on this page
            form_fields = page.widgets()
            
            for field in form_fields:
                field_info = {
                    'page': page_num + 1,
                    'field_name': field.field_name,
                    'field_type': field.field_type_string,
                    'field_value': field.field_value,
                    'rect': list(field.rect),
                }
                fields.append(field_info)
                
        return fields
 def _parse_xml_data(self, root):
    """Parse XML data from XFA - extract only text content"""
    text_content = []
    
    def extract_text_only(element):
        """Recursively extract only text content, ignoring structure"""
        # Add element's text if it exists and is meaningful
        if element.text and element.text.strip():
            text_content.append(element.text.strip())
        
        # Add tail text if it exists
        if element.tail and element.tail.strip():
            text_content.append(element.tail.strip())
        
        # Process children
        for child in element:
            extract_text_only(child)
    
    extract_text_only(root)
    
    # Filter out technical/structural content
    filtered_content = []
    for text in text_content:
        # Skip JavaScript code, XML namespaces, and technical strings
        if not any(skip_pattern in text for skip_pattern in [
            'http://', 'https://', 'application/x-javascript',
            'GENERATED - DO NOT EDIT', 'xmlns:', 'xfa.', 'var ', 'function',
            'ColorFieldsValidation', '.className', '.presence', '.nodes'
        ]):
            # Only include non-empty, meaningful text
            if len(text) > 1 and not text.startswith('{'):
                filtered_content.append(text)
    
    # Return as a simple list or join into a single string
    return {
        'text_content': filtered_content,
        'combined_text': ' '.join(filtered_content)
    }

def _parse_xfa_data(self, xfa_data):
    """Parse raw XFA data - extract only text content"""
    try:
        # Try to parse as XML
        xml_str = xfa_data.decode('utf-8', errors='ignore')
        root = ET.fromstring(xml_str)
        return self._parse_xml_data(root)  # This will now return text-only
    except:
        # If XML parsing fails, try BeautifulSoup for text extraction
        try:
            soup = BeautifulSoup(xfa_data, 'xml')
            return self._parse_with_beautifulsoup_text_only(soup)
        except:
            # Return raw data as last resort
            return {'raw_data': xfa_data.decode('utf-8', errors='ignore')}

def _parse_with_beautifulsoup_text_only(self, soup):
    """Parse XFA data using BeautifulSoup - extract only text content"""
    text_content = []
    
    # Find all text content, excluding script and style elements
    for element in soup.find_all(text=True):
        text = element.strip()
        if text and not any(skip_pattern in text for skip_pattern in [
            'http://', 'https://', 'application/x-javascript',
            'GENERATED - DO NOT EDIT', 'xmlns:', 'xfa.', 'var ', 'function',
            'ColorFieldsValidation', '.className', '.presence', '.nodes'
        ]):
            if len(text) > 1:
                text_content.append(text)
    
    return {
        'text_content': text_content,
        'combined_text': ' '.join(text_content)
    }

    def _extract_xfa_from_array(self, xfa_array):
        """Extract XFA data from pikepdf Array object"""
        xfa_data = b""
        
        for i in range(0, len(xfa_array), 2):
            if i + 1 < len(xfa_array):
                # XFA arrays contain pairs: (name, stream)
                stream_obj = xfa_array[i + 1]
                if hasattr(stream_obj, 'read_bytes'):
                    xfa_data += stream_obj.read_bytes()
        
        return xfa_data
    
    def _parse_xfa_data(self, xfa_data):
        """Parse raw XFA data"""
        try:
            # Try to parse as XML
            xml_str = xfa_data.decode('utf-8', errors='ignore')
            root = ET.fromstring(xml_str)
            return self._parse_xml_data(root)
        except:
            # If XML parsing fails, try BeautifulSoup
            try:
                soup = BeautifulSoup(xfa_data, 'xml')
                return self._parse_with_beautifulsoup(soup)
            except:
                # Return raw data as last resort
                return {'raw_data': xfa_data.decode('utf-8', errors='ignore')}
    
    def _parse_with_beautifulsoup(self, soup):
        """Parse XFA data using BeautifulSoup"""
        data = {}
        
        # Find all elements with text content
        for element in soup.find_all():
            if element.string and element.string.strip():
                tag_path = ' > '.join([parent.name for parent in element.parents][::-1] + [element.name])
                data[tag_path] = element.string.strip()
        
        return data
    
    def extract_all_methods(self):
        """
        Try all extraction methods and combine results
        """
        print("🚀 Starting comprehensive XFA extraction...")
        
        all_results = {}
        
        # Method 1: PyMuPDF
        pymupdf_result = self.extract_with_pymupdf()
        if pymupdf_result:
            all_results['pymupdf'] = pymupdf_result
        
        # Method 2: pikepdf
        pikepdf_result = self.extract_with_pikepdf()
        if pikepdf_result:
            all_results['pikepdf'] = pikepdf_result
        
        return all_results
    
    def save_results(self, results, output_dir="extracted_data"):
        """Save extraction results to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as JSON
        json_file = os.path.join(output_dir, "xfa_extracted_data.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save as readable text
        text_file = os.path.join(output_dir, "xfa_extracted_data.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("XFA Form Data Extraction Results\n")
            f.write("=" * 50 + "\n\n")
            
            for method, data in results.items():
                f.write(f"Method: {method.upper()}\n")
                f.write("-" * 30 + "\n")
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        f.write(f"{key}: {value}\n")
                else:
                    f.write(f"{data}\n")
                
                f.write("\n")
        
        print(f"📁 Results saved to: {output_dir}")
        return json_file, text_file


def main():
    # Example usage
    pdf_path = "xfa-example.pdf"  # Replace with your PDF path
    
    if not os.path.exists(pdf_path):
        print("❌ PDF file not found. Please update the path.")
        return
    
    # Create extractor instance
    extractor = XFAExtractor(pdf_path)
    
    # Extract using all methods
    results = extractor.extract_all_methods()
    
    if results:
        # Save results
        json_file, text_file = extractor.save_results(results)
        
        # Print summary
        print("\n📊 EXTRACTION SUMMARY")
        print("=" * 50)
        
        for method, data in results.items():
            print(f"\n{method.upper()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        print(f"  {key}: {len(value)} items")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  Data extracted: {len(str(data))} characters")
        
        print(f"\n✅ Complete results saved to:")
        print(f"   JSON: {json_file}")
        print(f"   Text: {text_file}")
        
    else:
        print("❌ No data could be extracted from the XFA form")


if __name__ == "__main__":
    main()