# atividades.py
import json, os, shutil
import customtkinter as ctk
from tkinter import messagebox, filedialog
from interface import configurar_janela, garantir_pasta_data
from turmas import carregar_turmas


PASTA = garantir_pasta_data()
CAMINHO = os.path.join(PASTA, "atividades.json")
DESTINO = os.path.join(PASTA, "uploads")

if not os.path.exists(DESTINO):
    os.makedirs(DESTINO)

def carregar_atividades():
    if not os.path.exists(CAMINHO):
        return []
    try:
        with open(CAMINHO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def salvar_atividades(lista):
    with open(CAMINHO, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def abrir_atividades(app):
    """Tela de upload e consulta de atividades."""
    atividades = carregar_atividades()
    janela = ctk.CTkToplevel(app)
    configurar_janela(janela, "Upload de Atividades", "600x480")

    ctk.CTkLabel(janela, text="Upload e Consulta de Atividades", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    # Carregar turmas disponíveis
    turmas_brutas = carregar_turmas()
    turmas = []

    for t in turmas_brutas:
        if isinstance(t, dict):
            turmas.append(t.get("nome", "Turma"))
        else:
            turmas.append(str(t))
    if not turmas:
        turmas = ["Nenhuma turma cadastrada"]
    ctk.CTkLabel(janela, text="Selecione a Turma:").pack(pady=(10, 2))

    turma_var = ctk.StringVar(value=turmas[0])
    turma_combo = ctk.CTkComboBox(janela, values=turmas, variable=turma_var, width=300)
    turma_combo.pack(pady=5)

    def selecionar_arquivo():
        caminho = filedialog.askopenfilename(title="Selecionar arquivo", filetypes=[("Todos os arquivos", "*.*")])
        if caminho:
            arquivo_var.set(caminho)

    ctk.CTkButton(janela, text="Selecionar Arquivo", command=selecionar_arquivo).pack(pady=4)

    def salvar():
        turma = turma_entry.get().strip()
        desc = desc_entry.get().strip()
        origem = arquivo_var.get()

        if not (turma and desc and os.path.exists(origem)):
            messagebox.showwarning("Atenção", "Preencha os campos e selecione um arquivo válido.")
            return

        nome_arquivo = os.path.basename(origem)
        destino_final = os.path.join(DESTINO, nome_arquivo)
        shutil.copy2(origem, destino_final)

        atividades.append({
            "turma": turma,
            "descricao": desc,
            "arquivo": nome_arquivo
        })
        salvar_atividades(atividades)
        messagebox.showinfo("Sucesso", f"Atividade '{desc}' registrada!")
        janela.destroy()

    ctk.CTkButton(janela, text="Salvar Atividade", width=220, height=40, command=salvar).pack(pady=8)

    # Exibe atividades registradas
    ctk.CTkLabel(janela, text="Atividades Cadastradas:").pack(pady=8)
    lista = ctk.CTkTextbox(janela, width=520, height=200)
    lista.pack(pady=4)

    if atividades:
        for a in atividades:
            lista.insert("end", f"Turma: {a['turma']}\nDescrição: {a['descricao']}\nArquivo: {a['arquivo']}\n---\n")
    else:
        lista.insert("end", "Nenhuma atividade cadastrada ainda.")
