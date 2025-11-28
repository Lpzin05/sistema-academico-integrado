# login.py
# Tela de login que usa usuarios.autenticar e abre dashboard (usando o mesmo app)
import customtkinter as ctk
from tkinter import messagebox
from usuarios import autenticar_usuario, adicionar_usuario
from dashboard import abrir_dashboard
from interface import iniciar_tema

def criar_tela_login(app):
    """
    Recebe o 'app' principal (CTk) criado no main.py;
    cria o frame de login e cuida de mudar entre login/cadastro.
    """
    # limpa app
    for w in app.winfo_children():
        w.destroy()

    frame = ctk.CTkFrame(app, width=560, height=440, corner_radius=15)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    titulo = ctk.CTkLabel(frame, text="Login do Sistema Acadêmico", font=ctk.CTkFont(size=20, weight="bold"))
    titulo.pack(pady=(30, 10))

    ctk.CTkLabel(frame, text="Usuário:").pack(pady=(8,0))
    entry_usuario = ctk.CTkEntry(frame, width=360)
    entry_usuario.pack(pady=5)

    ctk.CTkLabel(frame, text="Senha:").pack(pady=(8,0))
    entry_senha = ctk.CTkEntry(frame, width=360, show="*")
    entry_senha.pack(pady=5)

    modo = {"valor": "login"}

    def entrar_ou_cadastrar(event=None):
        usuario = entry_usuario.get().strip()
        senha = entry_senha.get().strip()
        if usuario == "" or senha == "":
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        if modo["valor"] == "login":
            if autenticar_usuario(usuario, senha):
                # abre dashboard no mesmo app
                abrir_dashboard(app, usuario)
            else:
                messagebox.showerror("Erro", "Usuário ou senha incorretos.")
        else:
            ok = adicionar_usuario(usuario, senha)
            if not ok:
                messagebox.showwarning("Aviso", "Usuário já existe.")
            else:
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                mudar_para_login()

    def mudar_para_cadastro():
        modo["valor"] = "cadastro"
        titulo.configure(text="Cadastro de Novo Usuário")
        botao_acao.configure(text="Cadastrar")
        texto_trocar.configure(text="Já possui uma conta?")
        botao_trocar.configure(text="Fazer Login", command=mudar_para_login)
        entry_usuario.delete(0, "end")
        entry_senha.delete(0, "end")

    def mudar_para_login():
        modo["valor"] = "login"
        titulo.configure(text="Login do Sistema Acadêmico")
        botao_acao.configure(text="Entrar")
        texto_trocar.configure(text="Ainda não tem conta?")
        botao_trocar.configure(text="Cadastrar", command=mudar_para_cadastro)
        entry_usuario.delete(0, "end")
        entry_senha.delete(0, "end")

    botao_acao = ctk.CTkButton(frame, text="Entrar", width=220, command=entrar_ou_cadastrar)
    botao_acao.pack(pady=(18,8))

    texto_trocar = ctk.CTkLabel(frame, text="Ainda não tem conta?")
    texto_trocar.pack(pady=(10,5))

    botao_trocar = ctk.CTkButton(frame, text="Cadastrar", width=140, height=32, fg_color="transparent",
                                 border_width=2, text_color=("gray90", "#DCE4EE"), command=mudar_para_cadastro)
    botao_trocar.pack()

    ctk.CTkButton(frame, text="Sair", width=140, height=32, fg_color="red", hover_color="#b30000", command=app.destroy).pack(pady=(20,6))

    entry_usuario.bind("<Return>", entrar_ou_cadastrar)
    entry_senha.bind("<Return>", entrar_ou_cadastrar)
