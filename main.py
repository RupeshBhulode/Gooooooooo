from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from supadata import Supadata, SupadataError

# Initialize FastAPI app
app = FastAPI(title="Supadata Transcript API")

# Initialize the Supadata client
supadata = Supadata(api_key="sd_0ae31fca72274fbc1482b0a4ff5a05ee")

# Request model
class TranscriptRequest(BaseModel):
    url: str
    lang: str = "hi"  # Default to Hindi
    text: bool = True
    mode: str = "auto"

# Response models
class TranscriptResponse(BaseModel):
    status: str
    language: str
    content: str

class AsyncTranscriptResponse(BaseModel):
    status: str
    job_id: str
    message: str

class ErrorResponse(BaseModel):
    status: str
    error_code: str
    error_message: str
    documentation_url: str = None

@app.get("/")
def read_root():
    return {
        "message": "Supadata Transcript API",
        "endpoints": {
            "POST /transcript": "Get transcript from video URL"
        }
    }

@app.post("/transcript", response_model=TranscriptResponse | AsyncTranscriptResponse)
async def get_transcript(request: TranscriptRequest):
    """
    Get transcript from video URL (YouTube, TikTok, Instagram, X/Twitter, or file URL)
    
    - **url**: Video URL from supported platforms
    - **lang**: Language preference (default: "hi" for Hindi)
    - **text**: Return plain text (default: True)
    - **mode**: Transcription mode (default: "auto")
    """
    try:
        # Get the transcript using the universal transcript method
        transcript = supadata.transcript(
            url=request.url,
            lang=request.lang,
            text=request.text,
            mode=request.mode
        )
        
        # Check if results are immediate or async
        if hasattr(transcript, 'content'):
            # Immediate results
            return TranscriptResponse(
                status="success",
                language=transcript.lang,
                content=transcript.content
            )
        else:
            # Async processing (large files)
            return AsyncTranscriptResponse(
                status="processing",
                job_id=transcript.job_id,
                message="Transcript is being processed. Use the job_id to check status."
            )
    
    except SupadataError as error:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_code": error.error,
                "error_message": error.message,
                "documentation_url": error.documentation_url if hasattr(error, 'documentation_url') else None
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "internal_error",
                "error_message": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)