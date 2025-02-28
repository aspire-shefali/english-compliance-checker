from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import aiofiles
import uvicorn

app = FastAPI()

SAVE_DIRECTORY = "uploaded_files"
os.makedirs(SAVE_DIRECTORY, exist_ok=True)

PERMITTED_FILE_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}

BUFFER_SIZE = 10 * 1024 * 1024  # 10MB


def check_file_type(uploaded_file: UploadFile):
    """Ensures the file type is either PDF or Word document."""
    if uploaded_file.content_type not in PERMITTED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only PDF and Word documents are accepted."
        )


@app.post("/upload")
async def handle_file_upload(uploaded_file: UploadFile = File(...)):
    """Processes file uploads, validates type, and writes data in chunks."""
    check_file_type(uploaded_file)

    destination_path = os.path.join(SAVE_DIRECTORY, uploaded_file.filename)

    try:
        async with aiofiles.open(destination_path, "wb") as output_file:
            while chunk := await uploaded_file.read(BUFFER_SIZE):
                await output_file.write(chunk)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(error)}") from error

    return JSONResponse(content={"filename": uploaded_file.filename, "message": "File successfully uploaded."})

if __name__ == "__main__":
    uvicorn.run("document_upload:app", host="127.0.0.1", port=8000, reload=True)