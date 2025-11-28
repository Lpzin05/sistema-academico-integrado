# dashboard.py
# Painel principal integrado com alunos, turmas, aulas, atividades e assistente IA

import customtkinter as ctk

from alunos import adicionar_aluno, buscar_aluno, ordenar_alunos_por_nota, gerar_relatorio
from turmas import adicionar_turma
from aulas import abrir_aulas
from atividades import abrir_atividades
from assistente_ia import abrir_assistente


def abrir_dashboard(app, usuario):
    """
    Esta função é chamada pela tela de login.
    Ela limpa a janela e monta o painel principal.
    """

    # Remove todos os widgets da janela
    for w in app.winfo_children():
        w.destroy()

    # ==========================
    # CABEÇALHO
    # ==========================
    header = ctk.CTkFrame(app, height=80)
    header.pack(fill="x")

    ctk.CTkLabel(
        header,
        text="Sistema Acadêmico - Painel Principal",
        font=ctk.CTkFont(size=20, weight="bold")
    ).pack(side="left", padx=20, pady=20)

    ctk.CTkLabel(
        header,
        text=f"Usuário: {usuario}",
        font=ctk.CTkFont(size=12)
    ).pack(side="right", padx=20)

    # ==========================
    # CORPO PRINCIPAL
    # ==========================
    body = ctk.CTkFrame(app)
    body.pack(padx=20, pady=20, fill="both", expand=True)

    # --------------------------
    # COLUNA ESQUERDA — ALUNOS
    # --------------------------
    left = ctk.CTkFrame(body)
    left.pack(side="left", padx=20, pady=20, fill="y")

    ctk.CTkLabel(left, text="Alunos", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    ctk.CTkButton(left, text="Cadastrar Aluno", width=260, command=lambda: adicionar_aluno(app)).pack(pady=6)
    ctk.CTkButton(left, text="Buscar Aluno", width=260, command=lambda: buscar_aluno(app)).pack(pady=6)
    ctk.CTkButton(left, text="Ordenar por Nota", width=260, command=lambda: ordenar_alunos_por_nota(app)).pack(pady=6)
    ctk.CTkButton(left, text="Gerar Relatório", width=260, command=lambda: gerar_relatorio(app)).pack(pady=6)

    # --------------------------
    # COLUNA DIREITA — TURMAS / AULAS / ATIVIDADES / IA
    # --------------------------
    right = ctk.CTkFrame(body)
    right.pack(side="right", padx=20, pady=20, fill="y")

    ctk.CTkLabel(right, text="Turmas e Aulas", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    ctk.CTkButton(right, text="Cadastrar Turma", width=260, command=lambda: adicionar_turma(app)).pack(pady=6)
    ctk.CTkButton(right, text="Gerenciar Aulas", width=260, command=lambda: abrir_aulas(app)).pack(pady=6)
    ctk.CTkButton(right, text="Upload / Atividades", width=260, command=lambda: abrir_atividades(app)).pack(pady=6)

    # --------------------------
    # BOTÃO DO ASSISTENTE IA
    # --------------------------
    ctk.CTkButton(
        right,
        text="Assistente IA",
        width=260,
        fg_color="#1e88e5",
        hover_color="#1565c0",
        command=lambda: abrir_assistente(app)
    ).pack(pady=15)

    # ==========================
    # RODAPÉ
    # ==========================
    footer = ctk.CTkFrame(app, height=60)
    footer.pack(fill="x", side="bottom")

    ctk.CTkButton(
        footer,
        text="Sair",
        width=140,
        fg_color="red",
        hover_color="#8b0000",
        command=app.destroy
    ).pack(pady=10)
