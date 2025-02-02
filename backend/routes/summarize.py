from flask import Blueprint, request, jsonify
from ..models.nlp_processing import NLPProcessor

summarize_bp = Blueprint('summarize', __name__)
nlp_processor = NLPProcessor()

@summarize_bp.route('/summarize', methods=['POST'])
def summarize_text():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        # Get parameters
        text = data['text']
        note_id = data.get('note_id')
        max_length = data.get('max_length')
        min_length = data.get('min_length')
        
        # Generate summary
        result = nlp_processor.generate_summary(
            text=text,
            note_id=note_id,
            max_length=max_length,
            min_length=min_length
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@summarize_bp.route('/analyze', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        # Perform various analyses
        sentiment = nlp_processor.analyze_sentiment(text)
        topics = nlp_processor.extract_topics(text)
        tags = nlp_processor.generate_tags(text)
        
        return jsonify({
            'success': True,
            'result': {
                'sentiment': sentiment,
                'topics': topics,
                'tags': tags
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500