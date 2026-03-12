from flask import Flask, render_template, request, jsonify
import os
import json
from threading import Lock
from datetime import datetime

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
DATA_LOCK = Lock()


def load_markers():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_markers(markers):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(markers, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/markers', methods=['GET'])
def get_markers():
    with DATA_LOCK:
        return jsonify(load_markers())


@app.route('/markers', methods=['POST'])
def add_marker():
    data = request.get_json(force=True, silent=True) or {}

    with DATA_LOCK:
        markers = load_markers()

        marker_id = len(markers) + 1

        marker = {
            'id': marker_id,
            'lat': data.get('lat'),
            'lng': data.get('lng'),
            'category': data.get('category', 'danger'),
            'type': data.get('type', 'drone'),
            'note': (data.get('note') or '').strip()[:120],
            'timestamp': datetime.utcnow().isoformat()
        }

        if marker['lat'] is None or marker['lng'] is None:
            return jsonify({'error': 'Missing coordinates'}), 400

        markers.append(marker)
        save_markers(markers)

    return jsonify({'status': 'ok'})


@app.route('/delete_marker/<int:marker_id>', methods=['DELETE'])
def delete_marker(marker_id):
    with DATA_LOCK:
        markers = load_markers()
        markers = [m for m in markers if m.get('id') != marker_id]
        save_markers(markers)

    return jsonify({'status': 'deleted'})


@app.route('/markers', methods=['DELETE'])
def clear_markers():
    with DATA_LOCK:
        save_markers([])
    return jsonify({'status': 'cleared'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
