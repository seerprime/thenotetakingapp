from flask import Blueprint, request, jsonify
from ..models.query_engine import QueryEngine

query_bp = Blueprint('query', __name__)
query_engine = QueryEngine()

@query_bp.route('/query', methods=['POST'])
def process_query():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        query = data['query']
        note_id = data.get('note_id')
        max_tokens = data.get('max_tokens', 150)
        
        # Process query
        result = query_engine.query(
            query=query,
            note_id=note_id,
            max_tokens=max_tokens
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@query_bp.route('/query/with-citations', methods=['POST'])
def query_with_citations():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        query = data['query']
        note_id = data.get('note_id')
        
        # Get answer with citations
        result = query_engine.get_answer_with_citations(
            query=query,
            note_id=note_id
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@query_bp.route('/suggest-questions', methods=['POST'])
def suggest_questions():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data or 'answer' not in data or 'context' not in data:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        questions = query_engine.suggest_followup_questions(
            query=data['query'],
            answer=data['answer'],
            context=data['context'],
            num_questions=data.get('num_questions', 3)
        )
        
        return jsonify({
            'success': True,
            'questions': questions
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500