import os
from docx2pdf import convert
from fastapi import APIRouter, File, UploadFile
from io import BytesIO
import base64
import fitz  # PyMuPDF

docx_router = APIRouter()

@docx_router.post("/api/upload_docx/")
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

        # Convert DOCX to PDF
        pdf_path = os.path.join(temp_dir, f"temp_{file.filename.replace('.docx', '.pdf')}")
        print(f"Starting conversion of DOCX to PDF...")

        try:
            # Perform conversion
            convert(docx_path, pdf_path)
        except Exception as conversion_error:
            print(f"Error during DOCX to PDF conversion: {conversion_error}")
            raise Exception("Failed to convert DOCX to PDF")

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

    finally:
        # Ensure Word application is properly closed by `docx2pdf`
        from comtypes.client import CreateObject
        try:
            word = CreateObject("Word.Application")
            word.Quit()
            print("Word application closed successfully")
        except Exception as word_error:
            print(f"Error while closing Word application: {word_error}")
