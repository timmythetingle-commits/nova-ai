"""Nova: server-side Groq tutoring API and web interface."""
import json
import os
import urllib.error
import urllib.request
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024
app.json.ensure_ascii = False
INSTRUCTIONS = '''You are Nova, a patient, knowledgeable tutor specializing in AP United States Government and Politics. Answer the student's actual question thoroughly and adapt to their level. Use conversation context to resolve follow-ups. Teach concepts, explain why and how they work, give concrete examples, distinguish commonly confused ideas, and offer a short practice question when useful. Cover all five units: foundations of American democracy; interactions among branches; civil liberties and civil rights; American political ideologies and beliefs; political participation. Connect constitutional principles, federalism, institutions, foundational documents, Supreme Court reasoning, public opinion, elections, parties, interest groups, and media. For FRQs, teach concept application, quantitative analysis, SCOTUS comparison, and argument essays. Explain claims, specific evidence, reasoning linking evidence to the claim, and responding to an alternate perspective. When reviewing work, identify strengths, missing reasoning, and concrete revisions. Do not invent official rubric points, quotations, case holdings, or current course requirements. Explain uncertainty and ask for the actual prompt/rubric for exact scoring. You have no live web access. Be politically balanced and separate facts from opinions. You can also help with other learning questions. Never tell students to use /teach to obtain an answer.'''

def configured():
    return bool(os.environ.get('GROQ_API_KEY', '').strip())

@app.get('/')
def home():
    return render_template('index.html', configured=configured())

@app.get('/health')
def health():
    return jsonify(status='ok', ai_configured=configured())

@app.post('/api/chat')
def chat():
    if not request.is_json:
        return jsonify(error='Send a JSON request.'), 415
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='Invalid JSON.'), 400
    message = data.get('message')
    history = data.get('history', [])
    if not isinstance(message, str) or not message.strip() or len(message) > 8000:
        return jsonify(error='Enter a message between 1 and 8000 characters.'), 400
    if not isinstance(history, list) or len(history) > 20:
        return jsonify(error='History must contain at most 20 messages.'), 400
    for item in history:
        if (not isinstance(item, dict) or item.get('role') not in ('user', 'assistant')
                or not isinstance(item.get('content'), str) or not 0 < len(item['content']) <= 16000):
            return jsonify(error='Invalid conversation history.'), 400
    if not configured():
        return jsonify(error='Nova is ready for an API connection. Set GROQ_API_KEY in the server environment to enable answers.'), 503
    body = dict(model=os.environ.get('GROQ_MODEL', 'openai/gpt-oss-20b'),
                messages=[{'role': 'system', 'content': INSTRUCTIONS}] +
                         [{'role': h['role'], 'content': h['content']} for h in history] +
                         [{'role': 'user', 'content': message.strip()}],
                max_completion_tokens=4096)
    upstream = urllib.request.Request('https://api.groq.com/openai/v1/chat/completions',
        data=json.dumps(body).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + os.environ['GROQ_API_KEY'].strip(),
                 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(upstream, timeout=75) as response:
            result = json.load(response)
        choices = result.get('choices') or []
        reply = choices[0].get('message', {}).get('content') if choices else None
        if not isinstance(reply, str):
            reply = ''
        if not reply.strip():
            return jsonify(error='Nova could not finish that answer. Please try again.'), 502
        return jsonify(reply=reply)
    except urllib.error.HTTPError as error:
        if error.code == 429:
            return jsonify(error='The AI service reached its usage limit. Please wait and try again, or check your Groq usage limits.'), 429
        if error.code in (401, 403):
            return jsonify(error='The server API credentials need attention. Check the key and model access.'), 503
        return jsonify(error='The AI service could not answer. Check the server model setting or try again later.'), 502
    except (TimeoutError, urllib.error.URLError):
        return jsonify(error='The AI service timed out or is unreachable. Please try again.'), 504
    except (ValueError, KeyError, TypeError):
        return jsonify(error='The AI service returned an unexpected response. Please try again.'), 502

@app.errorhandler(413)
def too_large(_error):
    return jsonify(error='Request is too large.'), 413

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', '10000')))
