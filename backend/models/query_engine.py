from typing import List, Dict, Optional
import openai
from .rag_database import RAGDatabase
from ..utils.config import OPENAI_API_KEY, TOP_K_RESULTS

class QueryEngine:
    def __init__(self):
        self.db = RAGDatabase()
        openai.api_key = OPENAI_API_KEY
    
    def _format_context(self, relevant_chunks: List[Dict]) -> str:
        """Format retrieved chunks into context string."""
        context_parts = []
        for chunk in relevant_chunks:
            context = f"Content: {chunk['content']}"
            if chunk['title']:
                context = f"Title: {chunk['title']}\n{context}"
            if chunk['start_time'] is not None:
                context += f"\n(Time: {chunk['start_time']:.2f}s - {chunk['end_time']:.2f}s)"
            context_parts.append(context)
        
        return "\n\n---\n\n".join(context_parts)
    
    def _generate_prompt(self, query: str, context: str) -> str:
        """Generate prompt for the LLM."""
        return f"""Please answer the question based on the provided context. If the context doesn't contain enough information to answer the question, please say so.

Context:
{context}

Question: {query}

Answer:"""
    
    def query(self, 
              query: str,
              note_id: Optional[int] = None,
              max_tokens: int = 150) -> Dict:
        """Process a query and return relevant answer."""
        try:
            # Retrieve relevant chunks
            if note_id:
                # If note_id provided, limit search to specific note
                note = self.db.get_note(note_id)
                if not note:
                    raise ValueError(f"Note with ID {note_id} not found")
                relevant_chunks = self.db.search(query, k=TOP_K_RESULTS)
                relevant_chunks = [c for c in relevant_chunks if c["note_id"] == note_id]
            else:
                # Search across all notes
                relevant_chunks = self.db.search(query, k=TOP_K_RESULTS)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": []
                }
            
            # Format context from retrieved chunks
            context = self._format_context(relevant_chunks)
            
            # Generate prompt
            prompt = self._generate_prompt(query, context)
            
            # Get response from LLM
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            # Format sources
            sources = []
            for chunk in relevant_chunks:
                source = {
                    "content": chunk["content"],
                    "note_id": chunk["note_id"],
                    "score": chunk["score"]
                }
                if chunk["start_time"] is not None:
                    source["timestamp"] = {
                        "start": chunk["start_time"],
                        "end": chunk["end_time"]
                    }
                sources.append(source)
            
            return {
                "answer": response.choices[0].message["content"].strip(),
                "sources": sources
            }
            
        except Exception as e:
            raise RuntimeError(f"Query processing failed: {str(e)}")
    
    def suggest_followup_questions(self, 
                                 query: str,
                                 answer: str,
                                 context: str,
                                 num_questions: int = 3) -> List[str]:
        """Generate follow-up questions based on the current Q&A."""
        prompt = f"""Based on the following question, answer, and context, suggest {num_questions} relevant follow-up questions that would help explore the topic further.

Previous Question: {query}
Answer: {answer}
Context: {context}

Follow-up Questions:"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate relevant follow-up questions based on the previous Q&A."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            # Parse response into list of questions
            questions_text = response.choices[0].message["content"]
            questions = [q.strip() for q in questions_text.split("\n") if q.strip() and "?" in q]
            
            return questions[:num_questions]
            
        except Exception:
            return []  # Return empty list if suggestion generation fails
    
    def get_answer_with_citations(self, 
                                query: str,
                                note_id: Optional[int] = None) -> Dict:
        """Get answer with specific citations to source material."""
        # Get basic answer first
        result = self.query(query, note_id)
        
        if not result["sources"]:
            return result
        
        # Generate new prompt requesting citations
        context = self._format_context(result["sources"])
        prompt = f"""Please answer the question and explicitly cite the relevant parts of the context using square brackets.

Context:
{context}

Question: {query}

Answer with citations:"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Provide answers with explicit citations to the source material using square brackets."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            result["answer_with_citations"] = response.choices[0].message["content"].strip()
            return result
            
        except Exception:
            return result  # Return original result if citation generation fails