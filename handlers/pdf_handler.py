from fastapi import APIRouter, File, UploadFile
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
        os.makedirs(temp_dir, exist_ok=True)

        contents = await file.read()
        pdf_path = os.path.join(temp_dir, f"temp_{file.filename}")

        with open(pdf_path, "wb") as f:
            f.write(contents)
        
        print(f"File saved at {pdf_path}")

        if not os.path.exists(pdf_path):
            return {"error": f"File not found at {pdf_path}"}

        # Open the PDF with PyMuPDF
        doc = fitz.open(pdf_path)

        image_previews = []  # Store base64-encoded images
        extracted_text = []   # Store extracted text

        for page_num in range(len(doc)):  # Process all pages
            page = doc.load_page(page_num)  

            # Extract text
            text = page.get_text("text").strip()
            if text:
                extracted_text.append(text)

            # Generate image preview
            pix = page.get_pixmap(dpi=300)  # Higher DPI for better quality
            img_bytes = pix.tobytes("png")  
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            image_previews.append(f"data:image/png;base64,{img_base64}")

        doc.close()
        os.remove(pdf_path)

        # Combine extracted text into a single string
        full_text = "\n\n".join(extracted_text)

        print(f"Returning image previews and extracted text")
        return {
            "previews": image_previews,  # All pages as images
            "content": full_text  # Full extracted text
        }

    except Exception as e:
        print(f"Error during file processing: {e}")
        return {"error": str(e)}
