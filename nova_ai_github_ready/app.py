"""Flask web frontend for the small offline Python intent chatbot."""
import os
from flask import Flask, jsonify, render_template, request
from python_ai_chatbot import IntentAI, load_knowledge

app = Flask(__name__)
app.json.ensure_ascii = False
bot = IntentAI(load_knowledge())

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/health')
def health():
    return jsonify({'status': 'ok'})

@app.post('/api/chat')
def chat():
    if not request.is_json:
        return jsonify({'error': 'Send a JSON request.'}), 415
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({'error': 'Invalid JSON.'}), 400
    message = payload.get('message')
    if not isinstance(message, str) or not message.strip():
        return jsonify({'error': 'Please enter a message.'}), 400
    if len(message) > 1000:
        return jsonify({'error': 'Messages must be 1000 characters or fewer.'}), 400
    return jsonify({'reply': bot.reply(message.strip())})

@app.errorhandler(413)
def too_large(_error):
    return jsonify({'error': 'Request is too large.'}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '10000')))
