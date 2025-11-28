# turmas.py
# Cadastro simples de turmas (modal)
import json
import os
import customtkinter as ctk
from tkinter import messagebox
from interface import configurar_janela, garantir_pasta_data

PASTA = garantir_pasta_data()
CAMINHO = os.path.join(PASTA, "turmas.json")

def carregar_turmas():
    if not os.path.exists(CAMINHO):
        return []
    try:
        with open(CAMINHO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def salvar_turmas(lista):
    if not os.path.exists(PASTA):
        os.makedirs(PASTA)
    with open(CAMINHO, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def adicionar_turma(app):
    turmas = carregar_turmas()
    janela = ctk.CTkToplevel(app)
    configurar_janela(janela, "Cadastro de Turma", "420x320")

    ctk.CTkLabel(janela, text="Cadastro de Turma", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=12)
    nome_entry = ctk.CTkEntry(janela, width=360, placeholder_text="Ex: 3ºA")
    nome_entry.pack(pady=6)
    prof_entry = ctk.CTkEntry(janela, width=360, placeholder_text="Professor responsável")
    prof_entry.pack(pady=6)
    turno_var = ctk.StringVar(value="Matutino")
    turno_menu = ctk.CTkOptionMenu(janela, values=["Matutino", "Vespertino", "Noturno"], variable=turno_var)
    turno_menu.pack(pady=6)

    def salvar():
        nome = nome_entry.get().strip()
        prof = prof_entry.get().strip()
        turno = turno_var.get()
        if not nome or not prof:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        # checar duplicado
        if any(t.get("nome","").lower() == nome.lower() for t in turmas):
            messagebox.showwarning("Aviso", "Turma já cadastrada.")
            return
        turmas.append({"nome": nome, "professor": prof, "turno": turno})
        salvar_turmas(turmas)
        messagebox.showinfo("Sucesso", f"Turma '{nome}' cadastrada!")
        janela.destroy()

    ctk.CTkButton(janela, text="Salvar", width=220, height=40, command=salvar).pack(pady=(12,6))
    ctk.CTkButton(janela, text="Cancelar", width=220, fg_color="gray", command=janela.destroy).pack()
