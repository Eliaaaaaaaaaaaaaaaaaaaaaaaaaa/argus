from flask import Flask, render_template, request, jsonify
import os
import json
from threading import Lock
from datetime import datetime

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
DATA_LOCK = Lock()


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"markers": [], "areas": []}

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Altes Format: nur Marker als Liste
            if isinstance(data, list):
                return {
                    "markers": data,
                    "areas": []
                }

            # Neues Format: Dict mit markers + areas
            if isinstance(data, dict):
                return {
                    "markers": data.get("markers", []),
                    "areas": data.get("areas", [])
                }

            return {"markers": [], "areas": []}
    except Exception:
        return {"markers": [], "areas": []}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


# --------------------
# MARKERS
# --------------------

@app.route('/markers', methods=['GET'])
def get_markers():
    with DATA_LOCK:
        data = load_data()
        return jsonify(data["markers"])


@app.route('/markers', methods=['POST'])
def add_marker():
    data_in = request.get_json(force=True, silent=True) or {}

    lat = data_in.get('lat')
    lng = data_in.get('lng')

    if lat is None or lng is None:
        return jsonify({'error': 'Missing coordinates'}), 400

    with DATA_LOCK:
        data = load_data()
        markers = data["markers"]

        marker_id = max((m.get('id', 0) for m in markers), default=0) + 1

        marker = {
            'id': marker_id,
            'lat': lat,
            'lng': lng,
            'category': data_in.get('category', 'danger'),
            'type': data_in.get('type', 'drone'),
            'note': (data_in.get('note') or '').strip()[:120],
            'timestamp': datetime.utcnow().isoformat()
        }

        markers.append(marker)
        data["markers"] = markers
        save_data(data)

    return jsonify({'status': 'ok', 'marker': marker})


@app.route('/delete_marker/<int:marker_id>', methods=['DELETE'])
def delete_marker(marker_id):
    with DATA_LOCK:
        data = load_data()
        data["markers"] = [m for m in data["markers"] if m.get('id') != marker_id]
        save_data(data)

    return jsonify({'status': 'deleted'})


@app.route('/markers', methods=['DELETE'])
def clear_markers():
    with DATA_LOCK:
        data = load_data()
        data["markers"] = []
        save_data(data)

    return jsonify({'status': 'cleared'})


# --------------------
# AREAS
# --------------------

@app.route('/areas', methods=['GET'])
def get_areas():
    with DATA_LOCK:
        data = load_data()
        return jsonify(data["areas"])


@app.route('/areas', methods=['POST'])
def add_area():
    data_in = request.get_json(force=True, silent=True) or {}
    points = data_in.get('points', [])

    if not isinstance(points, list) or len(points) < 3:
        return jsonify({'error': 'At least 3 points are required'}), 400

    cleaned_points = []
    for point in points:
        if not isinstance(point, list) or len(point) != 2:
            return jsonify({'error': 'Invalid point format'}), 400

        lat, lng = point

        if lat is None or lng is None:
            return jsonify({'error': 'Invalid coordinates in points'}), 400

        cleaned_points.append([lat, lng])

    with DATA_LOCK:
        data = load_data()
        areas = data["areas"]

        area_id = max((a.get('id', 0) for a in areas), default=0) + 1

        area = {
            'id': area_id,
            'category': data_in.get('category', 'danger'),
            'type': data_in.get('type', 'troops'),
            'note': (data_in.get('note') or '').strip()[:120],
            'points': cleaned_points,
            'timestamp': datetime.utcnow().isoformat()
        }

        areas.append(area)
        data["areas"] = areas
        save_data(data)

    return jsonify({'status': 'ok', 'area': area})


@app.route('/delete_area/<int:area_id>', methods=['DELETE'])
def delete_area(area_id):
    with DATA_LOCK:
        data = load_data()
        data["areas"] = [a for a in data["areas"] if a.get('id') != area_id]
        save_data(data)

    return jsonify({'status': 'deleted'})


@app.route('/areas', methods=['DELETE'])
def clear_areas():
    with DATA_LOCK:
        data = load_data()
        data["areas"] = []
        save_data(data)

    return jsonify({'status': 'cleared'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
