from fastapi import FastAPI, UploadFile, File
import shutil
import os
from analyzer import analyze_video

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Bowling Analysis API Running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = analyze_video(file_path)
    except Exception as e:
        return {"error": str(e)}

    return result