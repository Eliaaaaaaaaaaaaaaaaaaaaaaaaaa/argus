# ARGUS Tactical Map

Render-ready Flask-Prototyp einer einfachen Tactical Map.

## Lokal starten

```bash
pip install -r requirements.txt
python app.py
```

Dann im Browser öffnen:

```text
http://127.0.0.1:8000
```

## Render Deploy

- Repo auf GitHub hochladen
- Auf Render als Web Service verbinden
- `render.yaml` wird automatisch erkannt

## Endpoints

- `/` Web App
- `/health` Health Check
- `/markers` GET/POST/DELETE

## Hinweis

Das ist ein Demo-Prototyp und **nicht** militärisch sicher.
