
from flask import Flask, render_template, request, jsonify
import os, json

app = Flask(__name__)

DATA_FILE = "data.json"

def load_markers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_markers(markers):
    with open(DATA_FILE, "w") as f:
        json.dump(markers, f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/markers", methods=["GET"])
def get_markers():
    return jsonify(load_markers())

@app.route("/markers", methods=["POST"])
def add_marker():
    data = request.json
    markers = load_markers()
    markers.append(data)
    save_markers(markers)
    return jsonify({"status": "ok"})

@app.route("/markers", methods=["DELETE"])
def clear_markers():
    save_markers([])
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
