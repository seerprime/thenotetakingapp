from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from ..models.whisper_model import WhisperTranscriber
from ..utils.config import Config, ALLOWED_EXTENSIONS

transcribe_bp = Blueprint('transcribe', __name__)
transcriber = WhisperTranscriber()

@transcribe_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not file.filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get additional parameters
        language = request.form.get('language')
        task = request.form.get('task', 'transcribe')
        
        # Perform transcription
        result = transcriber.transcribe_audio(
            filepath,
            language=language,
            task=task
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
        
    finally:
        # Clean up uploaded file
        if 'filepath' in locals():
            try:
                os.remove(filepath)
            except:
                pass

@transcribe_bp.route('/transcribe/batch', methods=['POST'])
def transcribe_batch():
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        if not files:
            return jsonify({'error': 'No selected files'}), 400
        
        filepaths = []
        results = []
        
        # Save all files
        for file in files:
            if file.filename and file.filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
                filename = secure_filename(file.filename)
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(filepath)
                filepaths.append(filepath)
        
        # Perform batch transcription
        if filepaths:
            results = transcriber.transcribe_batch(
                filepaths,
                language=request.form.get('language'),
                task=request.form.get('task', 'transcribe')
            )
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
        
    finally:
        # Clean up uploaded files
        for filepath in filepaths:
            try:
                os.remove(filepath)
            except:
                pass