from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supadata import Supadata
import os

app = FastAPI(title="Supadata Transcript API")

API_KEY = os.getenv("SUPADATA_API_KEY", "sd_0ae31fca72274fbc1482b0a4ff5a05ee")
supadata = Supadata(api_key=API_KEY)

class TranscriptRequest(BaseModel):
    url: str
    lang: str = "hi"
    text: bool = True
    mode: str = "auto"

def extract_video_id(url: str) -> str:
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com' in url and 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    return url.split('/')[-1].split('?')[0]

@app.get("/")
def read_root():
    return {"message": "Supadata Transcript API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/transcript")
async def get_transcript(request: TranscriptRequest):
    try:
        url_lower = request.url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            video_id = extract_video_id(request.url)
            transcript = supadata.youtube.transcript(video_id=video_id, lang=request.lang, text=request.text)
        else:
            transcript = supadata.get_transcript(url=request.url, lang=request.lang, text=request.text, mode=request.mode)
        
        if hasattr(transcript, 'content'):
            return {
                "status": "success",
                "language": getattr(transcript, 'lang', request.lang),
                "content": transcript.content
            }
        else:
            return {
                "status": "processing",
                "job_id": getattr(transcript, 'job_id', None),
                "message": "Processing"
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
