# PteroPanel — Minecraft Node Manager (Flask)

A Flask web app for managing Pterodactyl-style Minecraft hosting nodes.

## Project Structure

```
pterodactyl_flask/
├── app.py               # Flask app + REST API routes
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # Frontend (Jinja2 template)
└── README.md
```

## Setup & Run

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the development server
python app.py
```

Then open http://localhost:5000 in your browser.

## API Endpoints

| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| GET    | `/api/nodes`                    | List all nodes + stats       |
| POST   | `/api/nodes`                    | Create a new node            |
| DELETE | `/api/nodes/<node_id>`          | Delete a node                |
| POST   | `/api/nodes/<node_id>/toggle`   | Toggle node online/offline   |
| POST   | `/api/nodes/refresh`            | Simulate live metric refresh |
| GET    | `/api/allocations`              | List all port allocations    |
| GET    | `/api/allocations?node_id=...`  | Filter allocations by node   |

## POST /api/nodes — Request Body

```json
{
  "name": "US-East-Node-3",
  "ip": "192.168.1.100",
  "loc": "US East",
  "ram": 64,
  "disk": 500,
  "port_start": 25565,
  "port_end": 25600
}
```

## Production Notes

- Replace the in-memory `NODES` / `ALLOCATIONS` lists with a proper database (SQLite, PostgreSQL, etc.)
- Use `gunicorn` instead of Flask's dev server: `gunicorn app:app`
- Add authentication before exposing publicly
- Set `FLASK_ENV=production` and a strong `SECRET_KEY` in environment variables
