# servidor.py
"""
Servidor TCP para LAN - Suporte a múltiplos clientes simultâneos.
Requisitos atendidos:
- Bind em 0.0.0.0 para aceitar conexões da rede local (LAN).
- Threads por conexão para atender clientes simultâneos.
- Lock para escrita concorrente em data/alunos.json.
- Logs detalhados (timestamp, IP:porta, ação).
- Escrita atômica em arquivo (temp -> replace).
- Resposta ao cliente ("OK" ou mensagem de erro).
"""

import socket
import json
import os
import threading
import traceback
import datetime
import signal
import sys
from typing import Dict, Any

HOST = "0.0.0.0"
PORT = 5050
DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "alunos.json")
TEMP_FILE = os.path.join(DATA_FOLDER, "alunos.tmp.json")

# Lock para proteger leitura/escrita concorrente do arquivo JSON
file_lock = threading.Lock()

# Conjunto (thread-safe via lock_clients) para rastrear clientes conectados
active_clients = set()
lock_clients = threading.Lock()

# Helper de timestamp
def ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_data_folder():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

def read_alunos() -> list:
    """Lê lista de alunos do JSON; retorna lista vazia se inexistente ou inválido."""
    ensure_data_folder()
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Em caso de arquivo inválido, tenta recuperar como lista vazia
        print(f"[{ts()}] [WARN] Arquivo JSON inválido - recuperando lista vazia.")
        return []

def write_alunos_atomic(alunos: list) -> None:
    """Grava o JSON de forma atômica: escreve em temp e substitui."""
    ensure_data_folder()
    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        json.dump(alunos, f, indent=4, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    # substitui atomically
    os.replace(TEMP_FILE, DATA_FILE)

def salvar_no_central(dados: Dict[str, Any]):
    """Salva o registro recebido em JSON, com lock para concorrência."""
    try:
        with file_lock:
            alunos = read_alunos()
            alunos.append(dados)
            write_alunos_atomic(alunos)
        print(f"[{ts()}] [SALVO] Registro armazenado em {DATA_FILE}")
    except Exception as e:
        print(f"[{ts()}] [ERRO AO SALVAR] {e}")
        traceback.print_exc()

def log(msg: str):
    print(f"[{ts()}] {msg}")

def tratar_cliente(conn: socket.socket, addr):
    client_id = f"{addr[0]}:{addr[1]}"
    with lock_clients:
        active_clients.add(client_id)
    log(f"[NOVO CLIENTE] {client_id} — Conexões ativas: {len(active_clients)}")

    try:
        # Recebe dados (limite razoável)
        data = conn.recv(4096)
        if not data:
            log(f"[IGNORADO] Conexão sem dados de {client_id}")
            return

        texto = data.decode("utf-8", errors="replace").strip()
        log(f"[RECEBIDO] De {client_id}: {texto}")

        # Esperamos formato: nome;turma;nota  (compatível com cliente C original)
        partes = texto.split(";")
        if len(partes) != 3:
            log(f"[FORMATO INVÁLIDO] {client_id} enviou formato inesperado.")
            try:
                conn.sendall("ERR: formato inválido. Use nome;turma;nota".encode("utf-8"))
            except:
                pass
            return

        nome, turma, nota_txt = partes
        try:
            nota = float(nota_txt)
        except:
            log(f"[DADO INVÁLIDO] Nota inválida de {client_id}: {nota_txt}")
            try:
                conn.sendall("ERR: nota inválida".encode("utf-8"))

            except:
                pass
            return

        registro = {"nome": nome.strip(), "turma": turma.strip(), "nota": round(nota, 2),
                    "origem_ip": addr[0], "origem_port": addr[1], "recebido_em": ts()}

        # Salva com proteção de concorrência
        salvar_no_central(registro)

        # Envia confirmação
        try:
            conn.sendall(b"OK")
            log(f"[RESPOSTA] OK enviado para {client_id}")
        except Exception as e:
            log(f"[ERRO] Falha ao enviar resposta para {client_id}: {e}")

    except Exception as e:
        log(f"[ERRO NO TRATAMENTO] Cliente {client_id}: {e}")
        traceback.print_exc()
    finally:
        try:
            conn.close()
        except:
            pass
        with lock_clients:
            if client_id in active_clients:
                active_clients.remove(client_id)
        log(f"[DESCONECTADO] {client_id} — Conexões ativas: {len(active_clients)}")

def iniciar_servidor():
    """Inicia o servidor e aceita conexões em loop; cria threads para cada cliente."""
    ensure_data_folder()
    log("============================================")
    log("  SERVIDOR ACADÊMICO - TCP (MULTI-CLIENTES)")
    log("============================================")
    servidor = None
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen(50)  # backlog maior para suportar bursts
        log(f"[ONLINE] Aguardando conexões em {HOST}:{PORT}")
        log("[INFO] Pressione Ctrl+C para encerrar o servidor.")

        while True:
            try:
                conn, addr = servidor.accept()
                # Cada cliente tratado em thread separada
                threading.Thread(target=tratar_cliente, args=(conn, addr), daemon=True).start()
            except KeyboardInterrupt:
                log("[ENCERRANDO] Recebido Ctrl+C. Encerrando servidor.")
                break
            except Exception as e:
                log(f"[ERRO ACCEPT] {e}")
                traceback.print_exc()

    except Exception as e:
        log("[ERRO FATAL] Não foi possível iniciar o servidor:")
        log(str(e))
        traceback.print_exc()
    finally:
        try:
            if servidor:
                servidor.close()
        except:
            pass
        log("[FINALIZADO] Servidor encerrado.")

# Tratamento de sinal para encerrar graciosamente (Windows/Linux)
def _signal_handler(sig, frame):
    log("[SINAL] Encerrando servidor via sinal.")
    try:
        # apenas encerrar o processo; o finally em iniciar_servidor() cuidará do fechamento
        sys.exit(0)
    except SystemExit:
        os._exit(0)

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

if __name__ == "__main__":
    iniciar_servidor()
