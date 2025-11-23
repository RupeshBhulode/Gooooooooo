from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supadata import Supadata
import os
import traceback

# Initialize FastAPI app
app = FastAPI(title="Supadata Transcript API")

# Get API key from environment variable or use default
API_KEY = os.getenv("SUPADATA_API_KEY", "sd_0ae31fca72274fbc1482b0a4ff5a05ee")
supadata = Supadata(api_key=API_KEY)

# Request model
class TranscriptRequest(BaseModel):
    url: str
    lang: str = "hi"
    text: bool = True
    mode: str = "auto"

@app.get("/")
def read_root():
    return {
        "message": "Supadata Transcript API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API information",
            "POST /transcript": "Get transcript from video URL",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/transcript")
async def get_transcript(request: TranscriptRequest):
    """
    Get transcript from video URL
    """
    try:
        transcript = supadata.transcript(
            url=request.url,
            lang=request.lang,
            text=request.text,
            mode=request.mode
        )
        
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
                "message": "Transcript is being processed."
            }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "error_code": "validation_error",
            "error_message": str(e)
        })
    
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail={
            "status": "error",
            "error_code": "connection_error",
            "error_message": "Unable to connect to Supadata API"
        })
    
    except Exception as e:
        # Log the full error for debugging
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "error_code": "internal_error",
            "error_message": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
