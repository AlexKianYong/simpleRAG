"""
Simple Flask web UI for TNGD FAQ Bot.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import initialize_bot, load_knowledge_base, ask_tngd_bot

app = Flask(__name__)

# Initialize bot on startup
try:
    initialize_bot()
    print("✅ Bot initialized successfully")
    
    # Load knowledge base
    faq_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'faq_data.json')
    load_knowledge_base(faq_file)
    print("✅ Knowledge base loaded successfully")
except Exception as e:
    print(f"❌ Failed to initialize bot: {e}")


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def ask_api():
    """API endpoint for asking questions."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'error': 'Question cannot be empty'
            }), 400
        
        result = ask_tngd_bot(question)
        
        return jsonify({
            'question': result['question'],
            'answer': result['final_answer'],
            'blocked': result['blocked'],
            'chunk_count': len(result['retrieved_chunks'])
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'TNGD FAQ Bot is running'
    }), 200


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" " * 20 + "TNGD FAQ Bot - Web UI")
    print("="*70)
    print("\n🌐 Starting web server...")
    print("📍 Open browser at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*70 + "\n")
    
    app.run(debug=True, host='localhost', port=5000)
