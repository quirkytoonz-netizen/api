from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import shutil
import os

app = FastAPI()

# Lovable integration ke liye CORS enable karna
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/mutate-video/")
async def mutate_video(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.mp4', '.mkv', '.mov', '.avi')):
        raise HTTPException(status_code=400, detail="Invalid video format")

    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(OUTPUT_DIR, f"safe_{file.filename}")

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Advanced Multi-Layer Mutation Command
    # - vf: Horizontal flip + 4% contrast boost + 1% brightness shift + speed adjustment
    # - af: Audio sample rate alteration + synchronization filter to prevent echo
    ffmpeg_cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "hflip,eq=contrast=1.04:brightness=0.01:saturation=1.02,setpts=0.96*PTS",
        "-af", "asetrate=45000*1.04,atempo=0.96",
        "-r", "29.97",
        "-vcodec", "libx264", "-crf", "20",  # High quality, low compression loss
        "-acodec", "aac", "-b:a", "192k",
        "-y", output_path
    ]

    try:
        result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print("FFmpeg Error Out:", result.stderr)
            raise HTTPException(status_code=500, detail="FFmpeg mutation failed")

        if os.path.exists(input_path):
            os.remove(input_path)
        
        return {
            "status": "success",
            "message": "Video successfully processed with Advanced Hybrid Mutation!",
            "file_path": output_path
        }
    
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=str(e))
