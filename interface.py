# interface.py
# Funções utilitárias para criar/configurar janelas com comportamento modal
import customtkinter as ctk
import os

def iniciar_tema():
    """Configura o tema global (chame no main)."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

def configurar_janela(janela, titulo, tamanho="400x300"):
    """
    Padroniza o comportamento das janelas secundárias:
    - título, tamanho
    - não redimensionável
    - traz para frente, foca e bloqueia a principal (modal)
    """
    janela.title(titulo)
    janela.geometry(tamanho)
    janela.resizable(False, False)
    janela.lift()
    janela.focus_force()
    janela.grab_set()

def garantir_pasta_data():
    """Garante que a pasta 'data' exista; retorna o caminho abreviado."""
    if not os.path.exists("data"):
        os.makedirs("data")
    return "data"
