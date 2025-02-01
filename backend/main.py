from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles  
from fastapi.responses import FileResponse
from routes import query, summarize
from transformers import pipeline
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from io import BytesIO
import whisper

app = FastAPI()

# Routers
app.include_router(query.router)
app.include_router(summarize.router)

# Initialize Whisper model (you can choose the model size)
model = whisper.load_model("base")  # Use 'base' or 'large' based on your needs

app.mount("/static", StaticFiles(directory="E:\\thenotetakingapp\\frontend\\static"), name="static")

# Serve index.html as the landing page
@app.get("/", response_class=HTMLResponse)
async def read_index():
    # Path to your index.html file
    with open("E:\\thenotetakingapp\\frontend\\index.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard():
    with open("E:\\thenotetakingapp\\frontend\\dashboard.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)

# Endpoint 1: Transcribe Audio
@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Load and process the audio with Whisper
    try:
        audio = whisper.load_audio(file_location)
        audio = whisper.pad_or_trim(audio)

        # Transcribe the audio using Whisper
        result = model.transcribe(audio)
        transcription = result["text"]
    except Exception as e:
        return {"error": f"Error transcribing audio: {str(e)}"}

    # Clean up the file after processing
    os.remove(file_location)
    return {"transcription": transcription}

# Endpoint 2: Summarize Text
class SummarizeRequest(BaseModel):
    text: str

@app.post("/summarize/")
async def summarize(request: SummarizeRequest):
    # Use the Hugging Face summarization pipeline
    summary = summarizer(request.text, max_length=50, min_length=25, do_sample=False)
    return {"summary": [s['summary_text'] for s in summary]}

# Endpoint 3: Query using RAG
class QueryRequest(BaseModel):
    question: str

@app.post("/query/")
async def query(request: QueryRequest):
    # Mock response using a RAG model
    answer = "This is a mock answer generated using RAG."
    return {"answer": answer}
