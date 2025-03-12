from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app) #allows frontend to access the api

DB_NAME = "../honeypot_logs.db" #database path

def get_attack_logs():
    """fetch attack logs from sqlite database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, source_ip, port FROM attacks ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs

@app.route("/api/logs", methods=["GET"])
def fetch_logs():
    """api endpoint to fetch attack logs"""
    logs = get_attack_logs()
    attack_data = [{"id": log[0], "timestamp": log[1], "source_ip": log[2], "port": log[3]} for log in logs]
    return jsonify(attack_data)

if __name__ == "__main__":
    app.run(debug = True, port = 5000) #runs flask on port 5000

