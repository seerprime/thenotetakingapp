import whisper
import torch
from typing import Dict, Optional
from pathlib import Path
import numpy as np
from ..utils.config import WHISPER_MODEL
from ..utils.audio_processing import AudioProcessor

class WhisperTranscriber:
    def __init__(self):
        # Load Whisper model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.model = whisper.load_model(WHISPER_MODEL).to(self.device)
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {str(e)}")
        
        self.audio_processor = AudioProcessor()
    
    def transcribe_audio(self, 
                        audio_path: str,
                        language: Optional[str] = None,
                        task: str = "transcribe",
                        **kwargs) -> Dict:
        """
        Transcribe audio file using Whisper model.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., "en", "es")
            task: Either "transcribe" or "translate"
            **kwargs: Additional arguments for whisper model
        
        Returns:
            Dictionary containing transcription results
        """
        try:
            # Process audio
            audio, sr = self.audio_processor.process_audio_file(
                audio_path,
                remove_silence=True,
                reduce_noise=True
            )
            
            # Prepare options
            options = {
                "task": task,
                "language": language,
                **kwargs
            }
            
            # Run transcription
            result = self.model.transcribe(
                audio,
                **{k: v for k, v in options.items() if v is not None}
            )
            
            # Extract segments with timestamps
            segments = []
            for segment in result["segments"]:
                segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "confidence": float(segment["confidence"])
                })
            
            # Prepare response
            response = {
                "text": result["text"].strip(),
                "segments": segments,
                "language": result["language"],
                "duration": len(audio) / sr
            }
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def transcribe_batch(self, 
                        audio_paths: list,
                        **kwargs) -> list:
        """Batch transcription of multiple audio files."""
        results = []
        for audio_path in audio_paths:
            try:
                result = self.transcribe_audio(audio_path, **kwargs)
                results.append({
                    "path": audio_path,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "path": audio_path,
                    "success": False,
                    "error": str(e)
                })
        return results
    
    @staticmethod
    def save_transcription(transcription: Dict, 
                          output_path: str,
                          format: str = "txt") -> str:
        """Save transcription to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "txt":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcription["text"])
        else:
            import json
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(transcription, f, indent=2, ensure_ascii=False)
        
        return str(output_path)