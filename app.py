
from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__)

markers = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return {"status": "ok"}, 200

@app.route("/markers", methods=["GET"])
def get_markers():
    return jsonify(markers)

@app.route("/markers", methods=["POST"])
def add_marker():
    data = request.json
    markers.append(data)
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
