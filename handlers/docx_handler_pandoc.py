import os
import subprocess
from fastapi import APIRouter, File, UploadFile
from io import BytesIO
import base64
import fitz  # PyMuPDF

docx_router_pandoc = APIRouter()

def convert_docx_to_pdf(docx_path: str, pdf_path: str):
    try:
        # Use LibreOffice to convert DOCX to PDF
        command = [
            "libreoffice", 
            "--headless",  # Run without GUI
            "--convert-to", "pdf", 
            "--outdir", os.path.dirname(pdf_path),
            docx_path
        ]
        subprocess.run(command, check=True)
        print(f"LibreOffice conversion successful. PDF saved at {pdf_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during DOCX to PDF conversion: {e}")
        raise Exception("Failed to convert DOCX to PDF using LibreOffice")

@docx_router_pandoc.post("/api/upload_docx_pandoc/")
async def upload_docx(file: UploadFile = File(...)):
    try:
        print(f"Received file: {file.filename}, type: {file.content_type}")
        
        # Ensure the temp_files directory exists
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Save the uploaded DOCX temporarily
        docx_path = os.path.join(temp_dir, f"temp_{file.filename}")
        contents = await file.read()
        with open(docx_path, "wb") as f:
            f.write(contents)
        
        print(f"File saved at {docx_path}")

        # Convert DOCX to PDF using LibreOffice
        pdf_path = os.path.join(temp_dir, f"temp_{file.filename.replace('.docx', '.pdf')}")
        print(f"Starting conversion of DOCX to PDF using LibreOffice...")

        # Perform conversion using LibreOffice
        convert_docx_to_pdf(docx_path, pdf_path)

        # Check if the PDF was successfully created
        if not os.path.exists(pdf_path):
            raise Exception("PDF conversion failed")

        print(f"PDF saved at {pdf_path}")

        # Read the PDF and convert it to an image (for preview)
        doc = fitz.open(pdf_path)

        # Prepare a list to hold base64-encoded image previews
        image_previews = []

        try:
            # Loop through all pages and convert them to images
            for page_num in range(min(3, len(doc))):  # Limiting to 3 pages for previews
                page = doc.load_page(page_num)  # Load the page
                pix = page.get_pixmap(dpi=300)  # Render the page as an image at 300 dpi
                img_bytes = pix.tobytes("png")  # Convert the image to PNG bytes
                
                # Encode the image in base64
                img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                image_previews.append(f"data:image/png;base64,{img_base64}")
        finally:
            # Ensure the PDF is closed
            doc.close()

        # Remove the temporary files
        os.remove(docx_path)
        os.remove(pdf_path)

        print(f"Returning image previews as base64")
        return {"previews": image_previews}

    except Exception as e:
        print(f"Error during file processing: {e}")
        return {"error": str(e)}
