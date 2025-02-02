from typing import List, Dict, Optional
import sqlite3
import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ..utils.config import (
    DATABASE_PATH,
    VECTOR_STORE_PATH,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

class RAGDatabase:
    def __init__(self):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = self._load_or_create_index()
        
        # Initialize SQLite connection
        self._init_database()
    
    def _load_or_create_index(self) -> faiss.IndexFlatL2:
        """Load existing FAISS index or create new one."""
        if Path(VECTOR_STORE_PATH).exists():
            try:
                return faiss.read_index(VECTOR_STORE_PATH)
            except:
                pass
        
        return faiss.IndexFlatL2(self.embedding_dim)
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    summary TEXT,
                    audio_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    content TEXT NOT NULL,
                    embedding_id INTEGER,
                    start_time REAL,
                    end_time REAL,
                    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
                )
            """)
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = " ".join(words[i:i + CHUNK_SIZE])
            chunks.append(chunk)
        
        return chunks
    
    def add_note(self, 
                 content: str,
                 title: Optional[str] = None,
                 summary: Optional[str] = None,
                 audio_path: Optional[str] = None,
                 segments: Optional[List[Dict]] = None) -> int:
        """Add new note and its embeddings to the database."""
        try:
            # Insert note
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO notes (title, content, summary, audio_path)
                    VALUES (?, ?, ?, ?)
                    """,
                    (title, content, summary, audio_path)
                )
                note_id = cursor.lastrowid
            
            # Process chunks and embeddings
            chunks = self._chunk_text(content)
            embeddings = self.embedding_model.encode(chunks)
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Save chunks and their mapping to embeddings
            with sqlite3.connect(DATABASE_PATH) as conn:
                for i, (chunk, embedding_id) in enumerate(zip(chunks, range(self.index.ntotal - len(chunks), self.index.ntotal))):
                    # Find corresponding segment times if available
                    start_time = None
                    end_time = None
                    if segments:
                        # Simple matching based on content overlap
                        for segment in segments:
                            if segment["text"] in chunk:
                                start_time = segment["start"]
                                end_time = segment["end"]
                                break
                    
                    conn.execute(
                        """
                        INSERT INTO chunks (note_id, content, embedding_id, start_time, end_time)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (note_id, chunk, embedding_id, start_time, end_time)
                    )
            
            # Save updated index
            faiss.write_index(self.index, VECTOR_STORE_PATH)
            
            return note_id
        
        except Exception as e:
            raise RuntimeError(f"Failed to add note to database: {str(e)}")
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for relevant chunks using RAG."""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding, k)
        
        # Fetch corresponding chunks
        results = []
        with sqlite3.connect(DATABASE_PATH) as conn:
            for i, idx in enumerate(indices[0]):
                chunk = conn.execute(
                    """
                    SELECT c.*, n.title, n.audio_path
                    FROM chunks c
                    JOIN notes n ON c.note_id = n.id
                    WHERE c.embedding_id = ?
                    """,
                    (int(idx),)
                ).fetchone()
                
                if chunk:
                    results.append({
                        "content": chunk[2],  # chunk content
                        "note_id": chunk[1],
                        "title": chunk[6],
                        "audio_path": chunk[7],
                        "start_time": chunk[4],
                        "end_time": chunk[5],
                        "score": float(1 / (1 + distances[0][i]))
                    })
        
        return results
    
    def get_note(self, note_id: int) -> Optional[Dict]:
        """Retrieve a specific note by ID."""
        with sqlite3.connect(DATABASE_PATH) as conn:
            note = conn.execute(
                "SELECT * FROM notes WHERE id = ?",
                (note_id,)
            ).fetchone()
            
            if note:
                return {
                    "id": note[0],
                    "title": note[1],
                    "content": note[2],
                    "summary": note[3],
                    "audio_path": note[4],
                    "created_at": note[5],
                    "updated_at": note[6]
                }
        return None
    
    def update_summary(self, note_id: int, summary: str):
        """Update the summary of a note."""
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute(
                """
                UPDATE notes 
                SET summary = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (summary, note_id)
            )