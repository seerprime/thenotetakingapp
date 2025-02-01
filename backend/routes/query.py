from fastapi import APIRouter
from pydantic import BaseModel
from models.rag_database import search, add_document

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class DocumentRequest(BaseModel):
    doc_id: str
    text: str

@router.post("/add_document/")
async def add_doc(request: DocumentRequest):
    add_document(request.doc_id, request.text)
    return {"message": "Document added successfully"}


@router.post("/query/")
async def query_rag(request: QueryRequest):
    results = search(request.query)
    return {"matches": results}
