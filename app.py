from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random
import copy

app = Flask(__name__)

# --- In-memory data store (replace with a real DB in production) ---

NODES = [
    {
        "id": "node-001",
        "name": "US-East-Prime",
        "loc": "New York, US",
        "status": "online",
        "ram": 72, "ram_used": 52,
        "disk": 800, "disk_used": 380,
        "cpu": 61,
        "servers": 8, "players": 64,
        "ip": "45.33.91.120",
        "color": "#43e6a2", "glow": "rgba(67,230,162,0.35)",
        "created_at": "2024-01-15",
    },
    {
        "id": "node-002",
        "name": "EU-Central-1",
        "loc": "Frankfurt, DE",
        "status": "online",
        "ram": 64, "ram_used": 28,
        "disk": 600, "disk_used": 210,
        "cpu": 34,
        "servers": 6, "players": 38,
        "ip": "88.99.14.55",
        "color": "#58a6ff", "glow": "rgba(88,166,255,0.35)",
        "created_at": "2024-02-01",
    },
    {
        "id": "node-003",
        "name": "US-West-Backup",
        "loc": "Los Angeles, US",
        "status": "online",
        "ram": 32, "ram_used": 29,
        "disk": 400, "disk_used": 360,
        "cpu": 88,
        "servers": 5, "players": 31,
        "ip": "172.104.2.87",
        "color": "#f85149", "glow": "rgba(248,81,73,0.35)",
        "created_at": "2024-02-20",
    },
    {
        "id": "node-004",
        "name": "APAC-SG-1",
        "loc": "Singapore",
        "status": "online",
        "ram": 48, "ram_used": 18,
        "disk": 500, "disk_used": 95,
        "cpu": 22,
        "servers": 4, "players": 14,
        "ip": "139.162.88.10",
        "color": "#ffd250", "glow": "rgba(255,210,80,0.35)",
        "created_at": "2024-03-05",
    },
    {
        "id": "node-005",
        "name": "AU-Sydney-1",
        "loc": "Sydney, AU",
        "status": "offline",
        "ram": 32, "ram_used": 0,
        "disk": 300, "disk_used": 0,
        "cpu": 0,
        "servers": 0, "players": 0,
        "ip": "45.79.202.33",
        "color": "#8b949e", "glow": "rgba(139,148,158,0.2)",
        "created_at": "2024-03-10",
    },
]

ALLOCATIONS = [
    {"ip": "45.33.91.120",  "port": 25565, "status": "used",    "node_id": "node-001"},
    {"ip": "45.33.91.120",  "port": 25566, "status": "used",    "node_id": "node-001"},
    {"ip": "45.33.91.120",  "port": 25567, "status": "free",    "node_id": "node-001"},
    {"ip": "88.99.14.55",   "port": 25565, "status": "used",    "node_id": "node-002"},
    {"ip": "88.99.14.55",   "port": 25566, "status": "free",    "node_id": "node-002"},
    {"ip": "172.104.2.87",  "port": 25565, "status": "used",    "node_id": "node-003"},
    {"ip": "172.104.2.87",  "port": 25566, "status": "used",    "node_id": "node-003"},
    {"ip": "139.162.88.10", "port": 25565, "status": "used",    "node_id": "node-004"},
    {"ip": "139.162.88.10", "port": 25566, "status": "free",    "node_id": "node-004"},
    {"ip": "45.79.202.33",  "port": 25565, "status": "offline", "node_id": "node-005"},
]

COLORS = ["#43e6a2", "#58a6ff", "#ffd250", "#f785b1", "#a371f7"]


def get_stats():
    online = sum(1 for n in NODES if n["status"] == "online")
    servers = sum(n["servers"] for n in NODES)
    players = sum(n["players"] for n in NODES)
    alerts = sum(1 for n in NODES if n["cpu"] > 80 or (n["ram"] and n["ram_used"] / n["ram"] > 0.9))
    return {
        "online_nodes": online,
        "total_nodes": len(NODES),
        "active_servers": servers,
        "players_online": players,
        "alerts": alerts,
    }


# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/nodes", methods=["GET"])
def get_nodes():
    return jsonify({"nodes": NODES, "stats": get_stats()})


@app.route("/api/nodes", methods=["POST"])
def create_node():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("ip"):
        return jsonify({"error": "name and ip are required"}), 400

    node_id = f"node-{len(NODES) + 1:03d}"
    color = COLORS[len(NODES) % len(COLORS)]
    new_node = {
        "id": node_id,
        "name": data["name"],
        "loc": data.get("loc", "Unknown"),
        "status": "online",
        "ram": int(data.get("ram", 32)),
        "ram_used": 0,
        "disk": int(data.get("disk", 300)),
        "disk_used": 0,
        "cpu": 0,
        "servers": 0,
        "players": 0,
        "ip": data["ip"],
        "color": color,
        "glow": color + "55",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }

    # Add port allocations if range provided
    port_start = int(data.get("port_start", 25565))
    port_end = int(data.get("port_end", port_start + 5))
    for port in range(port_start, min(port_end + 1, port_start + 36)):
        ALLOCATIONS.append({
            "ip": new_node["ip"],
            "port": port,
            "status": "free",
            "node_id": node_id,
        })

    NODES.append(new_node)
    return jsonify({"node": new_node, "stats": get_stats()}), 201


@app.route("/api/nodes/<node_id>", methods=["DELETE"])
def delete_node(node_id):
    node = next((n for n in NODES if n["id"] == node_id), None)
    if not node:
        return jsonify({"error": "Node not found"}), 404
    NODES.remove(node)
    ALLOCATIONS[:] = [a for a in ALLOCATIONS if a["node_id"] != node_id]
    return jsonify({"message": f"Node {node_id} deleted", "stats": get_stats()})


@app.route("/api/nodes/<node_id>/toggle", methods=["POST"])
def toggle_node(node_id):
    node = next((n for n in NODES if n["id"] == node_id), None)
    if not node:
        return jsonify({"error": "Node not found"}), 404

    if node["status"] == "online":
        node["status"] = "offline"
        node["cpu"] = 0
        node["ram_used"] = 0
        node["servers"] = 0
        node["players"] = 0
        for a in ALLOCATIONS:
            if a["node_id"] == node_id:
                a["status"] = "offline"
    else:
        node["status"] = "online"
        node["cpu"] = random.randint(10, 55)
        node["ram_used"] = int(node["ram"] * random.uniform(0.2, 0.5))
        node["servers"] = random.randint(1, 5)
        node["players"] = random.randint(1, 25)
        for a in ALLOCATIONS:
            if a["node_id"] == node_id:
                a["status"] = "free"

    return jsonify({"node": node, "stats": get_stats()})


@app.route("/api/nodes/refresh", methods=["POST"])
def refresh_nodes():
    """Simulate live metric updates for all online nodes."""
    for node in NODES:
        if node["status"] == "online":
            node["cpu"] = max(5, min(99, node["cpu"] + random.randint(-10, 10)))
            node["players"] = max(0, node["players"] + random.randint(-3, 3))
    return jsonify({"nodes": NODES, "stats": get_stats()})


@app.route("/api/allocations", methods=["GET"])
def get_allocations():
    node_id = request.args.get("node_id")
    allocs = [a for a in ALLOCATIONS if not node_id or a["node_id"] == node_id]
    return jsonify({"allocations": allocs})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
