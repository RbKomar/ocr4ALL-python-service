from fastapi import FastAPI, UploadFile, File, HTTPException # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import logging
import tempfile
from services.file_handler import save_uploaded_file, extract_zip, create_output_dir
from services.pdf_processor import process_pdfs, save_images_as_gray

logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

@app.post("/upload-zip/")
async def upload_zip(file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = save_uploaded_file(file, tmpdir)
            extract_zip(zip_path, tmpdir)
            
            pdf_paths = process_pdfs(tmpdir)
            for pdf_path in pdf_paths:
                output_dir = create_output_dir(pdf_path)
                save_images_as_gray(pdf_path, output_dir)
            
            logging.info(f"Processed all PDFs in {file.filename} successfully.")
    except Exception as e:
        logging.error(f"Error processing zip file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing zip file: {e}")
    
    return JSONResponse({"status": "success", "message": "Files processed and copied to OCR4all input directory."})

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)
