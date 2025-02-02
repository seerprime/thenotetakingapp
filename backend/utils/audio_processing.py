import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional
from .config import SAMPLE_RATE, MAX_AUDIO_LENGTH, ALLOWED_EXTENSIONS

class AudioProcessor:
    @staticmethod
    def is_valid_file(filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
        """Load and preprocess audio file."""
        try:
            # Load audio file
            audio, sr = librosa.load(file_path, sr=None)
            
            # Resample if necessary
            if sr != SAMPLE_RATE:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=SAMPLE_RATE)
            
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = librosa.to_mono(audio)
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Check duration
            duration = len(audio) / SAMPLE_RATE
            if duration > MAX_AUDIO_LENGTH:
                raise ValueError(f"Audio length exceeds maximum duration of {MAX_AUDIO_LENGTH} seconds")
            
            return audio, SAMPLE_RATE
        
        except Exception as e:
            raise RuntimeError(f"Error processing audio file: {str(e)}")
    
    @staticmethod
    def remove_silence(audio: np.ndarray, sr: int) -> np.ndarray:
        """Remove silence from audio."""
        # Get non-silent intervals
        intervals = librosa.effects.split(
            audio,
            top_db=30,
            frame_length=2048,
            hop_length=512
        )
        
        # Concatenate non-silent parts
        processed_audio = np.concatenate([audio[start:end] for start, end in intervals])
        return processed_audio
    
    @staticmethod
    def apply_noise_reduction(audio: np.ndarray) -> np.ndarray:
        """Apply basic noise reduction."""
        # Calculate noise profile from the first 1000ms
        noise_sample = audio[:int(SAMPLE_RATE)]
        noise_profile = np.mean(np.abs(noise_sample))
        
        # Apply simple noise gate
        threshold = noise_profile * 2
        audio[np.abs(audio) < threshold] = 0
        return audio
    
    @staticmethod
    def save_processed_audio(audio: np.ndarray, sr: int, output_path: str) -> str:
        """Save processed audio to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, audio, sr)
        return str(output_path)
    
    @classmethod
    def process_audio_file(cls, 
                          input_path: str, 
                          output_path: Optional[str] = None,
                          remove_silence: bool = True,
                          reduce_noise: bool = True) -> Tuple[np.ndarray, int]:
        """Complete audio processing pipeline."""
        # Validate file
        if not cls.is_valid_file(input_path):
            raise ValueError(f"Invalid file format. Allowed formats: {ALLOWED_EXTENSIONS}")
        
        # Load audio
        audio, sr = cls.load_audio(input_path)
        
        # Apply processing steps
        if reduce_noise:
            audio = cls.apply_noise_reduction(audio)
        
        if remove_silence:
            audio = cls.remove_silence(audio, sr)
        
        # Save if output path provided
        if output_path:
            cls.save_processed_audio(audio, sr, output_path)
        
        return audio, sr