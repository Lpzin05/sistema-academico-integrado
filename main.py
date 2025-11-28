# main.py
"""
Arquivo principal do sistema acadêmico.
- Inicializa o tema CustomTkinter
- Verifica se o servidor está ativo
- Se não estiver ativo, tenta iniciar automaticamente em background
- Abre a tela de login
- Compatível com executável PyInstaller
"""

import customtkinter as ctk
from login import criar_tela_login
from interface import iniciar_tema
import socket
import subprocess
import threading
import time
import os
import sys


# -------------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------------
PORT = 5050
SERVIDOR_SCRIPT = "servidor.py"


# -------------------------------------------------------------
# Função: detectar se o servidor está ativo
# -------------------------------------------------------------
def servidor_respondendo(host="127.0.0.1", port=PORT, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False


# -------------------------------------------------------------
# Executar servidor.py como processo background
# -------------------------------------------------------------
def iniciar_servidor_background():
    """Inicia o servidor localmente em processo separado sem travar a GUI."""

    def run():
        try:
            # Detecta o Python do executável PyInstaller ou do sistema
            python_exec = sys.executable

            # Se estiver em EXE, servidor.py estará extraído em uma pasta temp
            script_path = SERVIDOR_SCRIPT
            if getattr(sys, "frozen", False):
                script_path = os.path.join(sys._MEIPASS, SERVIDOR_SCRIPT)

            creation_flag = 0
            if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
                creation_flag = subprocess.CREATE_NO_WINDOW

            subprocess.Popen(
                [python_exec, script_path],
                creationflags=creation_flag,
                cwd=os.getcwd()
            )
        except Exception as e:
            print("[ERRO] Falha ao iniciar servidor automático:", e)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    # Espera até 6 tentativas (3 segundos)
    for _ in range(6):
        if servidor_respondendo():
            return True
        time.sleep(0.5)
    return False


# -------------------------------------------------------------
# Função principal da aplicação
# -------------------------------------------------------------
def main():
    iniciar_tema()

    print("[SISTEMA] Iniciando Sistema Acadêmico...")

    # Verifica servidor
    if not servidor_respondendo():
        print("[INFO] Nenhum servidor detectado. Tentando iniciar automaticamente...")
        iniciado = iniciar_servidor_background()

        if iniciado:
            print("[OK] Servidor iniciado com sucesso.")
        else:
            print("[AVISO] NÃO foi possível iniciar o servidor automaticamente.")
            print("Você pode iniciar o Servidor.exe manualmente.")
    else:
        print("[INFO] Servidor encontrado. Entrando em modo CLIENTE.")

    # ---------------------------------------------------------
    # INICIAR INTERFACE PRINCIPAL
    # ---------------------------------------------------------
    app = ctk.CTk()
    app.title("Sistema Acadêmico Integrado (Cliente/Servidor)")
    app.geometry("720x560")
    app.resizable(False, False)

    criar_tela_login(app)

    app.mainloop()


# Executar diretamente
if __name__ == "__main__":
    main()
