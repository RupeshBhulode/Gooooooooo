from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from supadata import Supadata
import time

# ⚠️ Hardcoded API Key — use only for local testing
SUPADATA_API_KEY = "sd_0ae31fca72274fbc1482b0a4ff5a05ee"

supadata = Supadata(api_key=SUPADATA_API_KEY)
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Supadata YouTube Transcript</title>
        </head>
        <body style="font-family: Arial; margin: 40px;">
            <h1>Supadata YouTube Transcript</h1>
            <form method="post" action="/">
                <label for="url">Enter YouTube URL:</label><br><br>
                <input type="text" id="url" name="url" style="width: 400px;" required />
                <br><br>
                <button type="submit">Get Transcript</button>
            </form>
        </body>
    </html>
    """


@app.post("/", response_class=HTMLResponse)
def get_transcript(url: str = Form(...)):
    try:
        transcript_result = supadata.transcript(
            url=url,
            lang="en",
            text=True,
            mode="auto"
        )

        status = "unknown"
        content = ""

        # If the response has a job_id → check status once
        if hasattr(transcript_result, "job_id"):
            result = supadata.transcript.get_job_status(transcript_result.job_id)
            status = getattr(result, "status", "unknown")

            if status == "completed":
                content = getattr(result, "content", "")
            else:
                content = f"Job is not completed yet. Status: {status}"

        else:
            status = "completed"
            content = str(transcript_result)

        return f"""
        <html>
            <body style="font-family: Arial; margin: 40px;">
                <h2>Transcript Result</h2>
                <p><strong>Status:</strong> {status}</p>
                <pre style="white-space: pre-wrap;">{content}</pre>
                <a href="/">Back</a>
            </body>
        </html>
        """

    except Exception as e:
        return f"""
        <html>
            <body style="font-family: Arial; margin: 40px;">
                <h2>Error</h2>
                <p>{str(e)}</p>
                <a href="/">Back</a>
            </body>
        </html>
        """


# JSON API version
@app.post("/api/transcript")
def transcript_json(url: str):
    try:
        transcript_result = supadata.transcript(url=url, lang="en", text=True, mode="auto")

        if hasattr(transcript_result, "job_id"):
            result = supadata.transcript.get_job_status(transcript_result.job_id)
            return {
                "status": getattr(result, "status", "unknown"),
                "content": getattr(result, "content", None),
            }

        return {
            "status": "completed",
            "content": str(transcript_result),
        }

    except Exception as e:
        return {"error": str(e)}

