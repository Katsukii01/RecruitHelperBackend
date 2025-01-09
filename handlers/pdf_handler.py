from fastapi import APIRouter, File, UploadFile
from io import BytesIO
import base64
import os
import fitz  # PyMuPDF

pdf_router = APIRouter()

@pdf_router.post("/api/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        print(f"Received file: {file.filename}, type: {file.content_type}")
        
        # Ensure the temp_files directory exists
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)  # Create the directory if it doesn't exist

        contents = await file.read()
        # Save the uploaded PDF temporarily
        pdf_path = os.path.join(temp_dir, f"temp_{file.filename}")
        with open(pdf_path, "wb") as f:
            f.write(contents)
        
        print(f"File saved at {pdf_path}")

        # Check if the file exists and is accessible
        if not os.path.exists(pdf_path):
            return {"error": f"File not found at {pdf_path}"}

        # Open the PDF with PyMuPDF
        doc = fitz.open(pdf_path)

        # Prepare a list to hold base64-encoded image previews
        image_previews = []

        # Loop through all pages and convert them to images
        for page_num in range(min(3, len(doc))):  # Limiting to 3 pages for previews
            page = doc.load_page(page_num)  # Load the page
            pix = page.get_pixmap(dpi=300)  # Render the page as an image at 300 dpi
            img_bytes = pix.tobytes("png")  # Convert the image to PNG bytes
            
            # Encode the image in base64
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            image_previews.append(f"data:image/png;base64,{img_base64}")

        # Explicitly close the document to release any file locks
        doc.close()

        # Remove the temporary PDF file
        os.remove(pdf_path)

        print(f"Returning image previews as base64")
        return {"previews": image_previews}

    except Exception as e:
        print(f"Error during file processing: {e}")
        return {"error": str(e)}
