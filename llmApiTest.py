import subprocess
import os

def flatten_xfa_with_pdftk(input_pdf):
    """Flatten XFA PDF using PDFtk - most reliable method"""
    try:
        output_pdf = input_pdf.replace('.pdf', '_flattened.pdf')
        # Split command into separate arguments
        cmd = ['pdftk', input_pdf, 'output', output_pdf, 'flatten']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully flattened XFA form to: {output_pdf}")
            return True
        else:
            print(f"PDFtk error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("PDFtk not installed. Install from: https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/")
        return False

# Add debug prints to check paths
print(f"Current working directory: {os.getcwd()}")
print(f"Checking if file exists: {os.path.exists('xfa-example.pdf')}")
flatten_xfa_with_pdftk('xfa-example.pdf')