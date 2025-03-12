import socket
import sqlite3
import logging
import threading

#Configure logging to store attack attempts
logging.basicConfig(filename="honeypot_logs.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

#List of ports to simulate an iot device
PORTS = [22, 23, 80]

DB_NAME = "honeypot_logs.db"

def initialize_db():
    """create the database table if it doesnt exist"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS attacks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                   source_ip TEXT,
                   port INTEGER
                   )''')
    conn.commit()
    conn.close()

def log_attack(source_ip, port):
    """log attack attempt in SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attacks (source_ip, port) VALUES (?, ?)", (source_ip, port))
    conn.commit()
    conn.close()

def handle_connection(client_socket, addr, port):
    """Handles an incoming connection, logs the attempt, sends a fake response."""
    try:
        logging.info(f"Connection attempt from {addr[0]} on port {port}")
        log_attack(addr[0], port) #save t0 database
        logging.getLogger().handlers[0].flush()

        if port == 22:
            response = "SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\n"
        elif port == 23:
            response = "Welcome to Telnet IoT Device\r\nLogin: "
        elif port == 80:
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>IoT Device</h1>"
        else:
            response = "Connection accepted"

        client_socket.send(response.encode()) #send fake response
    except Exception as e:
        print(f"Error handling connection: {e}")
    finally:
        client_socket.close() #close connection


def start_honeypot():
    """starts the honeypot and listens on multiple ports"""
    initialize_db() #ensures database is ready
    sockets = []

    for port in PORTS:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen(5)
        sockets.append(server)
        print(f"Honeypot listening on port {port}")

    while True:
        for server in sockets:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_connection, args=(client_socket, addr, server.getsockname()[1])).start()

if __name__ == "__main__":
    start_honeypot()