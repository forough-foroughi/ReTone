from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        text = request.form.get("text")
        tone = request.form.get("tone")
        # call the desired AI api
        # result = f"[{tone.upper()}] {text}"
        result = "Under structure :-)"
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)