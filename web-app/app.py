import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create Flask app
app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("RETONE_MODEL")

# Map simple UI tone keys to descriptive labels for the promp
TONE_MAP = {
    "serious":   "Serious / Sincere",
    "friendly":  "Friendly / Warm",
    "humorous":   "Playful / Light-hearted",
    "loving":  "Romantic / Affectionate",
}

# The output should be just "rewritten sentence"
SYSTEM = (
    "You rephrase a single sentence into the requested tone, "
    "keeping meaning, adding politeness and clarity. Output only the rewritten sentence."
)

# Render the HTML page (form + JS that POSTs to /api/retone)
@app.route("/")
def index():
    return render_template("index.html")

# 
@app.post("/api/retone")
def api_retone():

    data = request.get_json(force=True) or {}

    text = (data.get("text") or "").strip()
    tone_key = (data.get("tone") or "serious").strip()

    if not text:
        return jsonify(error = "text is required."), 400
    
    tone = TONE_MAP.get(tone_key, "Serious / Sincere")

    prompt = f"Tone: {tone}\nInput: {text}\nRewrite in that tone:"

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",   # API key from .env
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,                          # e.g., deepseek/deepseek-r1:free
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": prompt},
                ],
                "temperature": 0.3,                     # lower = more stable/consistent
            },
            timeout=30,
        )
        # Raise an HTTPError if status is not 2xx
        r.raise_for_status()

        # 7.7) Extract the generated text from the OpenRouter/OpenAI-compatible schema
        result = r.json()["choices"][0]["message"]["content"].strip()

        # 7.8) Return JSON back to the frontend
        return jsonify(result=result, tone=tone_key)

    except Exception as e:
        # Return error details for the UI to display
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run(debug=True)