from fastapi import APIRouter
from pydantic import BaseModel
from models.nlp_processing import summarize_text

router = APIRouter()

class SummarizeRequest(BaseModel):
    text: str

@router.post("/summarize/")
async def summarize(request: SummarizeRequest):
    """
    API endpoint to summarize text using NLP.
    """
    summary = summarize_text(request.text)
    return {"summary": summary}
