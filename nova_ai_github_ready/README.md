# Nova — Python AI chatbot (Render-ready)

A responsive website with a Flask API backed by a tiny offline Naive Bayes intent classifier. No external AI API key is needed.

> This is **not a large language model**. It chooses responses from trained categories. It is a learning/demo project, not a general-purpose AI assistant.

## Run locally

```bash
python -m pip install -r requirements.txt
python app.py
```

Open http://localhost:10000 in your browser. The website is served by Flask.

## Deploy to Render

1. Create a new GitHub repository and upload **all files and folders in this project** (the `app.py`, `render.yaml`, and `requirements.txt` files must be at the repository root).
2. In [Render Dashboard](https://dashboard.render.com/), select **New > Blueprint** and connect the repository. Render reads `render.yaml` and creates the Python web service.
3. Approve the service configuration and deploy.
4. When the deployment finishes, open the `https://<your-service-name>.onrender.com` address shown by Render.

### Manual Web Service alternative

Create a **Web Service**, connect the repository, select **Python 3**, and use:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn --bind 0.0.0.0:$PORT app:app`
- **Health check path:** `/health`

For a personal demo, you can select the Free compute plan if available.

## API

POST `/api/chat` with JSON `{"message":"hello"}`. Returns `{"reply":"Hello! What would you like to talk about?"}`.

GET `/health` returns a JSON health response.

## Limitations

- It only recognizes a few predefined topics; it cannot answer arbitrary questions like ChatGPT.
- The web app intentionally does not expose `/teach`, because allowing strangers to change the global chatbot's answers would make a public site unsafe and easy to abuse. To change its knowledge, edit `STARTER_DATA` in `python_ai_chatbot.py` and redeploy.
- The website doesn't retain chat messages on the server. A page refresh starts a new conversation.
- Render's free web services can sleep when idle. Their local files aren't durable, so saving knowledge to a file at runtime is unsuitable for persistent learning on the free plan. For persistence, use a database.
- Before sharing widely, add rate limits and other production security protections.
