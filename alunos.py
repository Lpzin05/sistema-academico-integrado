# alunos.py
"""
Módulo de gestão de alunos:
- carregar / salvar alunos (data/alunos.json)
- adicionar aluno (modal com Nome, Turma e Nota) -> integra com cliente C
- buscar aluno (lista atualizável em tempo real)
- ordenar por nota (maior -> menor)
- gerar_relatorio() em PDF (tabela formatada, cores e opção de abrir)
"""

import json
import os
import socket
import subprocess
import customtkinter as ctk
from tkinter import messagebox
from interface import configurar_janela, garantir_pasta_data

# ---------------------------------------------------------
# Caminhos e constantes
# ---------------------------------------------------------
PASTA = garantir_pasta_data()
CAMINHO_ALUNOS = os.path.join(PASTA, "alunos.json")
CAMINHO_TURMAS = os.path.join(PASTA, "turmas.json")
CAMINHO_RELATORIO = os.path.join(PASTA, "relatorio_alunos.json")
PDF_RELATORIO = os.path.join(PASTA, "relatorio_alunos.pdf")


# ---------------------------------------------------------
# Utilidades de persistência
# ---------------------------------------------------------
def carregar_alunos():
    """Lê alunos do JSON; retorna lista vazia se não existir ou inválido."""
    if not os.path.exists(CAMINHO_ALUNOS):
        return []
    try:
        with open(CAMINHO_ALUNOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def salvar_alunos(lista):
    """Salva lista de alunos no arquivo JSON (cria pasta se necessário)."""
    if not os.path.exists(PASTA):
        os.makedirs(PASTA)
    with open(CAMINHO_ALUNOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)


def carregar_turmas():
    """Lê turmas do JSON; retorna lista vazia se não existir."""
    if not os.path.exists(CAMINHO_TURMAS):
        return []
    try:
        with open(CAMINHO_TURMAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def servidor_ativo(host="127.0.0.1", port=5050, timeout=0.8):
    """Tenta abrir conexão curta com servidor; True se houver servidor."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False


# ---------------------------------------------------------
# ADICIONAR ALUNO
# ---------------------------------------------------------
def adicionar_aluno(app):
    """
    Abre modal para cadastrar aluno.
    Campos: Nome (Entry), Turma (OptionMenu), Nota (Entry).
    - Valida campos
    - Salva localmente em JSON
    - Se servidor ativo e cliente.exe existir, chama cliente.exe para enviar dados ao servidor
    """
    alunos = carregar_alunos()
    turmas = carregar_turmas()

    janela = ctk.CTkToplevel(app)
    configurar_janela(janela, "Cadastro de Aluno", "520x480")

    ctk.CTkLabel(
        janela,
        text="Cadastro de Aluno",
        font=ctk.CTkFont(size=20, weight="bold")
    ).pack(pady=12)

    # Nome
    ctk.CTkLabel(janela, text="Nome completo:", anchor="w").pack(fill="x", padx=30)
    nome_entry = ctk.CTkEntry(janela, width=420, placeholder_text="Digite o nome do aluno")
    nome_entry.pack(pady=6)

    # Turma (OptionMenu). Se não houver turmas, mostrar aviso na opção.
    ctk.CTkLabel(janela, text="Turma:", anchor="w").pack(fill="x", padx=30, pady=(8, 0))
    turma_values = [t["nome"] if isinstance(t, dict) and "nome" in t else str(t) for t in turmas] if turmas else []
    if not turma_values:
        turma_values = ["Nenhuma turma cadastrada"]
    turma_menu = ctk.CTkOptionMenu(janela, values=turma_values, width=300)
    turma_menu.set(turma_values[0])
    turma_menu.pack(pady=6)

    # Nota
    ctk.CTkLabel(janela, text="Nota (0 - 10):", anchor="w").pack(fill="x", padx=30, pady=(8, 0))
    nota_entry = ctk.CTkEntry(janela, width=200, placeholder_text="Ex: 8.5")
    nota_entry.pack(pady=6)

    def salvar(event=None):
        nome = nome_entry.get().strip()
        turma = turma_menu.get().strip()
        nota_txt = nota_entry.get().strip()

        if not nome or not turma or not nota_txt:
            messagebox.showwarning("Erro", "Preencha todos os campos.")
            return

        try:
            nota = float(nota_txt)
            if nota < 0 or nota > 10:
                raise ValueError
        except Exception:
            messagebox.showwarning("Erro", "Digite uma nota válida entre 0 e 10.")
            return

        # Salvar localmente
        alunos.append({"nome": nome, "turma": turma, "nota": round(nota, 2)})
        try:
            salvar_alunos(alunos)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar localmente: {e}")
            return

        # Tentar executar cliente.exe (módulo em C) para envio ao servidor
        cliente_exe = os.path.join(os.getcwd(), "cliente.exe")
        if servidor_ativo() and os.path.exists(cliente_exe):
            try:
                # Em Windows, usar CREATE_NO_WINDOW para não mostrar console extra
                creation_flags = 0
                if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
                    creation_flags = subprocess.CREATE_NO_WINDOW
                subprocess.Popen([cliente_exe, nome, turma, str(nota)], creationflags=creation_flags)
            except Exception as e:
                # Não bloquear a aplicação; apenas avisar
                messagebox.showwarning("Aviso", f"Falha ao executar cliente.exe: {e}")
        else:
            # Se servidor não ativo ou cliente não encontrado, já foi salvo localmente
            if not servidor_ativo():
                messagebox.showinfo("Aviso", "Servidor desligado — salvo apenas localmente.")
            else:
                messagebox.showinfo("Aviso", "Cliente (cliente.exe) não encontrado — salvo apenas localmente.")

        messagebox.showinfo("Sucesso", f"Aluno {nome} cadastrado com sucesso!")
        janela.destroy()

    # Botões
    btn_frame = ctk.CTkFrame(janela)
    btn_frame.pack(pady=12)
    ctk.CTkButton(btn_frame, text="Salvar", width=200, command=salvar).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Cancelar", width=200, fg_color="gray", command=janela.destroy).pack(side="right", padx=8)

    # Bind Enter
    janela.bind("<Return>", salvar)


# ---------------------------------------------------------
# BUSCAR ALUNO
# ---------------------------------------------------------
def buscar_aluno(app):
    """
    Abre modal para buscar alunos.
    Exibe todos inicialmente; filtra em tempo real conforme se digita.
    """
    alunos = carregar_alunos()

    janela = ctk.CTkToplevel(app)
    configurar_janela(janela, "Buscar Aluno", "560x520")

    ctk.CTkLabel(janela, text="Buscar Aluno", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)

    entrada = ctk.CTkEntry(janela, width=460, placeholder_text="Digite o nome ou parte do nome")
    entrada.pack(pady=8)

    resultado = ctk.CTkTextbox(janela, width=520, height=360)
    resultado.pack(pady=6)
    resultado.configure(state="disabled")

    def atualizar(event=None):
        termo = entrada.get().lower().strip()
        resultado.configure(state="normal")
        resultado.delete("1.0", "end")

        if termo == "":
            filtrados = alunos
        else:
            filtrados = [a for a in alunos if termo in a.get("nome", "").lower()]

        if not filtrados:
            resultado.insert("end", "Nenhum aluno encontrado.")
        else:
            for a in filtrados:
                resultado.insert("end", f"Nome: {a.get('nome','')}\nTurma: {a.get('turma','')}\nNota: {a.get('nota','')}\n\n")

        resultado.configure(state="disabled")

    # Mostra todos inicialmente
    atualizar()
    entrada.bind("<KeyRelease>", atualizar)
    entrada.bind("<Return>", atualizar)


# ---------------------------------------------------------
# ORDENAR POR NOTA
# ---------------------------------------------------------
def ordenar_alunos_por_nota(app):
    alunos = carregar_alunos()

    janela = ctk.CTkToplevel(app)
    configurar_janela(janela, "Alunos por Nota", "520x520")

    ctk.CTkLabel(janela, text="Alunos Ordenados por Nota (maior → menor)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    texto = ctk.CTkTextbox(janela, width=500, height=420)
    texto.pack(pady=6)
    texto.configure(state="normal")
    texto.delete("1.0", "end")

    ordenados = sorted(alunos, key=lambda a: float(a.get("nota", 0)), reverse=True)
    if not ordenados:
        texto.insert("end", "Nenhum aluno cadastrado.")
    else:
        for i, a in enumerate(ordenados, start=1):
            texto.insert("end", f"{i}. {a.get('nome','')} - {a.get('turma','')} - Nota: {a.get('nota','')}\n")

    texto.configure(state="disabled")


# ---------------------------------------------------------
# GERAR RELATÓRIO (PDF COMPLETO, TABELA, ABRIR AO FINAL)
# ---------------------------------------------------------
def gerar_relatorio(app):
    """
    Gera um PDF com resumo e tabela de alunos.
    Usa reportlab; se a biblioteca não existir, pede para instalar.
    Ao finalizar, pergunta ao usuário se quer abrir o PDF.
    """
    alunos = carregar_alunos()

    if not alunos:
        messagebox.showinfo("Relatório", "Nenhum aluno cadastrado.")
        return

    # tenta importar reportlab dinamicamente
    try:
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except Exception as e:
        messagebox.showerror("Biblioteca ausente", "A biblioteca 'reportlab' não está instalada.\n\n"
                             "Instale executando no terminal:\n"
                             "python -m pip install reportlab")
        return

    total = len(alunos)
    media = sum(float(a.get("nota", 0)) for a in alunos) / total
    maior = max(alunos, key=lambda x: float(x.get("nota", 0)))
    menor = min(alunos, key=lambda x: float(x.get("nota", 0)))

    nome_pdf = PDF_RELATORIO

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle("Titulo", parent=estilos["Title"], fontSize=18, alignment=1, spaceAfter=8)
    estilo_sub = ParagraphStyle("Sub", parent=estilos["Normal"], fontSize=11, spaceAfter=6)

    story = []
    story.append(Paragraph("Relatório de Alunos", estilo_titulo))
    story.append(Paragraph(f"Gerado em: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}", estilo_sub))
    story.append(Spacer(1, 8))

    story.append(Paragraph(f"Total de Alunos: <b>{total}</b>", estilo_sub))
    story.append(Paragraph(f"Média Geral das Notas: <b>{media:.2f}</b>", estilo_sub))
    story.append(Paragraph(f"Maior Nota: <b>{maior.get('nome','')}</b> - {maior.get('turma','')} ({maior.get('nota','')})", estilo_sub))
    story.append(Paragraph(f"Menor Nota: <b>{menor.get('nome','')}</b> - {menor.get('turma','')} ({menor.get('nota','')})", estilo_sub))
    story.append(Spacer(1, 12))

    # Tabela: cabeçalho + linhas
    dados_tabela = [["Nome do Aluno", "Turma", "Nota"]]
    # ordenar por nome para apresentar
    for a in sorted(alunos, key=lambda x: x.get("nome","").lower()):
        dados_tabela.append([a.get("nome",""), a.get("turma",""), f"{float(a.get('nota',0)):.1f}"])

    tabela = Table(dados_tabela, colWidths=[300, 90, 70])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F80ED")),  # azul cabeçalho
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
    ]))

    story.append(tabela)

    # Constrói PDF (com paginação automática do SimpleDocTemplate)
    try:
        doc = SimpleDocTemplate(nome_pdf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        doc.build(story)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao gerar PDF: {e}")
        return

    # Pergunta ao usuário se deseja abrir o PDF
    import webbrowser
    abrir = messagebox.askyesno("Relatório Gerado", f"Relatório salvo em:\n{nome_pdf}\n\nDeseja abrir agora?")
    if abrir:
        try:
            webbrowser.open(nome_pdf)
        except Exception as e:
            messagebox.showwarning("Aviso", f"Não foi possível abrir o PDF automaticamente: {e}\nCaminho: {nome_pdf}")