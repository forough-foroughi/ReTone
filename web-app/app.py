import os
import requests, time
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

# Create Flask app
app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("RETONE_MODEL")

REQUESTS = Counter("retone_http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY  = Histogram("retone_request_latency_seconds", "Latency(s)", ["route"])

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


@app.before_request
def _start_timer():
    request._t0 = time.perf_counter()


@app.after_request
def _record(resp):
    # stable route label (avoids high-cardinality)
    route = getattr(getattr(request, "url_rule", None), "rule", "unknown")
    # latency
    t0 = getattr(request, "_t0", None)
    if t0 is not None:
        LATENCY.labels(route=route).observe(time.perf_counter() - t0)
    # counters
    REQUESTS.labels(
        method=request.method,
        route=route,
        status=str(resp.status_code)
    ).inc()
    return resp


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# Render the HTML page (form + everything POSTs to /api/retone)
@app.get("/")
def index():
    return render_template("index.html")


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
                "Authorization": f"Bearer {API_KEY}",   
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

        # Extract the generated text from the AI-Engin schema
        result = r.json()["choices"][0]["message"]["content"].strip()

        # Return JSON back to the frontend
        return jsonify(result=result, tone=tone_key)

    except Exception as e:
        # Return error details for the UI to display
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)