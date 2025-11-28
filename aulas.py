# aulas.py
import os
import json
import customtkinter as ctk
from tkinter import messagebox
from interface import configurar_janela, garantir_pasta_data

PASTA = garantir_pasta_data()
CAMINHO_AULAS = os.path.join(PASTA, "aulas.json")
CAMINHO_TURMAS = os.path.join(PASTA, "turmas.json")


# ---------------------------
# utilitários de arquivo
# ---------------------------
def carregar_aulas():
    if not os.path.exists(CAMINHO_AULAS):
        return []
    try:
        with open(CAMINHO_AULAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salvar_aulas(lista):
    if not os.path.exists(PASTA):
        os.makedirs(PASTA)
    with open(CAMINHO_AULAS, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)


def carregar_turmas():
    if not os.path.exists(CAMINHO_TURMAS):
        return []
    try:
        with open(CAMINHO_TURMAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# ---------------------------
# Tela de Gerenciar Aulas
# ---------------------------
def abrir_aulas(app):
    # carrega dados
    aulas = carregar_aulas()
    turmas_brutas = carregar_turmas()

    # prepara lista de nomes de turmas
    turmas = []
    for t in turmas_brutas:
        if isinstance(t, dict):
            turmas.append(t.get("nome", "Turma"))
        else:
            turmas.append(str(t))
    if not turmas:
        turmas = ["Nenhuma turma cadastrada"]

    # janela modal
    janela = ctk.CTkToplevel(app)
    configurar_janela(janela, "Gerenciar Aulas", "750x800")

    # título
    ctk.CTkLabel(janela, text="Gerenciar Aulas", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(12, 6))

    # frame superior com Combobox e filtro (centralizado)
    frame_top = ctk.CTkFrame(janela)
    frame_top.pack(pady=8, padx=12, fill="x")

    # Turma
    lbl_turma = ctk.CTkLabel(frame_top, text="Turma:", anchor="w")
    lbl_turma.grid(row=0, column=0, sticky="w", padx=(8,6))
    turma_var = ctk.StringVar(value=turmas[0])
    turma_box = ctk.CTkComboBox(frame_top, values=turmas, variable=turma_var, width=220)
    turma_box.grid(row=0, column=1, padx=(0,12))

    # Filtro / campo onde usuário pode digitar texto de busca OU o índice da aula
    lbl_filtro = ctk.CTkLabel(frame_top, text="Filtro (texto ou índice):", anchor="w")
    lbl_filtro.grid(row=0, column=2, sticky="w", padx=(6,6))
    filtro_entry = ctk.CTkEntry(frame_top, width=260, placeholder_text="Digite texto para filtrar ou número da aula")
    filtro_entry.grid(row=0, column=3, padx=(0,8))

    # caixa de listagem (centralizada)
    lista = ctk.CTkTextbox(janela, width=640, height=300)
    lista.pack(pady=(10,12))

    # variável para manter o último conjunto filtrado (lista de referencias aos objetos)
    last_filtradas = []

    # função para atualizar a listagem com base na turma selecionada e no filtro de texto
    def atualizar_lista(event=None):
        nonlocal last_filtradas
        lista.configure(state="normal")
        lista.delete("1.0", "end")

        # recarrega aulas sempre para garantir sincronização com arquivo
        registros = carregar_aulas()

        turma_sel = turma_var.get()
        filtro_raw = filtro_entry.get().strip()
        filtro_txt = filtro_raw.lower()

        filtradas = []
        for a in registros:
            # filtra por turma (se existir turma selecionada)
            if turma_sel and turma_sel != "Nenhuma turma cadastrada":
                if a.get("turma") != turma_sel:
                    continue
            # filtra por texto no conteúdo, se houver texto e não for apenas número de índice
            if filtro_txt and not filtro_txt.isdigit():
                if filtro_txt not in a.get("conteudo", "").lower():
                    continue
            filtradas.append(a)

        last_filtradas = filtradas  # salva referência

        if not filtradas:
            lista.insert("end", "Nenhuma aula encontrada.\n")
        else:
            for idx, a in enumerate(filtradas):
                # mostra índices relativos ao conjunto filtrado — use este número para editar/excluir
                lista.insert("end",
                    f"[{idx}] Turma: {a.get('turma')}\n"
                    f"Conteúdo:\n{a.get('conteudo')}\n"
                    f"------------------------------\n"
                )

        lista.configure(state="disabled")

    # dispara atualização inicial
    atualizar_lista()

    # binds: filtro ao vivo e Enter para aplicar filtro
    filtro_entry.bind("<KeyRelease>", atualizar_lista)   # filtro AO VIVO
    filtro_entry.bind("<Return>", atualizar_lista)       # Enter também aplica

    # mudar turma também atualiza ao vivo
    turma_box.bind("<<ComboboxSelected>>", atualizar_lista)

    # ---------------------------
    # Formulário (conteúdo) para criar/editar
    # ---------------------------
    frame_form = ctk.CTkFrame(janela)
    frame_form.pack(pady=6, padx=12, fill="x")

    ctk.CTkLabel(frame_form, text="Conteúdo da Aula:", anchor="w").pack(anchor="w", padx=6, pady=(4,0))
    conteudo_box = ctk.CTkTextbox(frame_form, width=640, height=150)
    conteudo_box.pack(pady=(6,8))

    # quando ENTER estiver dentro do conteúdo, salva nova aula (comportamento padrão pedido)
    def enter_no_conteudo(event=None):
        salvar_nova_aula()
    conteudo_box.bind("<Return>", lambda e: enter_no_conteudo(e))

    # ---------------------------
    # Funções de seleção por índice (índice relativo ao filtered list)
    # ---------------------------
    def selecionar_indice_relativo():
        """Retorna (idx_relativo, idx_global) ou (None, None) se inválido."""
        val = filtro_entry.get().strip()
        if not val:
            messagebox.showwarning("Aviso", "Digite o número da aula no campo de filtro.")
            return None, None
        # se o usuário digitou um número, converte e valida contra last_filtradas
        try:
            idx_rel = int(val)
        except:
            messagebox.showwarning("Aviso", "Para editar/excluir digite o número (índice) da aula no campo de filtro.")
            return None, None

        if idx_rel < 0 or idx_rel >= len(last_filtradas):
            messagebox.showwarning("Aviso", "Índice fora do intervalo das aulas filtradas.")
            return None, None

        # localizar o índice global do objeto (primeira ocorrência)
        registros = carregar_aulas()
        aula_obj = last_filtradas[idx_rel]
        try:
            idx_global = registros.index(aula_obj)
        except ValueError:
            # fallback: procurar por igualdade de conteúdo/turma se objetos diferentes
            idx_global = None
            for i, r in enumerate(registros):
                if r.get("turma") == aula_obj.get("turma") and r.get("conteudo") == aula_obj.get("conteudo"):
                    idx_global = i
                    break
            if idx_global is None:
                messagebox.showerror("Erro", "Não foi possível localizar a aula selecionada nos registros.")
                return None, None

        return idx_rel, idx_global

    # ---------------------------
    # Ações: salvar nova, editar, salvar alteração, excluir
    # ---------------------------
    def salvar_nova_aula(event=None):
        turma = turma_var.get()
        conteudo = conteudo_box.get("1.0", "end").strip()

        if turma == "Nenhuma turma cadastrada":
            messagebox.showerror("Erro", "Cadastre uma turma antes de registrar aulas.")
            return

        if not conteudo:
            messagebox.showwarning("Erro", "Digite o conteúdo da aula.")
            return

        registros = carregar_aulas()
        registros.append({"turma": turma, "conteudo": conteudo})
        salvar_aulas(registros)
        conteudo_box.delete("1.0", "end")
        atualizar_lista()
        messagebox.showinfo("OK", "Aula registrada com sucesso!")

    def editar_aula():
        idx_rel, idx_global = selecionar_indice_relativo()
        if idx_rel is None:
            return
        registros = carregar_aulas()
        # carrega conteúdo atual na caixa para editar
        conteudo_box.delete("1.0", "end")
        conteudo_box.insert("1.0", registros[idx_global].get("conteudo", ""))
        # garante que a combo mostre a turma da aula selecionada
        turma_box.set(registros[idx_global].get("turma", turma_var.get()))
        messagebox.showinfo("Editar", "Altere o conteúdo e clique em 'Salvar Alteração'.")

    def salvar_alteracao():
        idx_rel, idx_global = selecionar_indice_relativo()
        if idx_rel is None:
            return
        novos_conteudo = conteudo_box.get("1.0", "end").strip()
        nova_turma = turma_var.get()
        if not novos_conteudo:
            messagebox.showwarning("Erro", "Digite algo para salvar na alteração.")
            return
        registros = carregar_aulas()
        registros[idx_global]["conteudo"] = novos_conteudo
        registros[idx_global]["turma"] = nova_turma
        salvar_aulas(registros)
        atualizar_lista()
        messagebox.showinfo("OK", "Aula alterada com sucesso!")

    def excluir_aula():
        idx_rel, idx_global = selecionar_indice_relativo()
        if idx_rel is None:
            return
        registros = carregar_aulas()
        # confirmação
        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir esta aula?"):
            return
        del registros[idx_global]
        salvar_aulas(registros)
        conteudo_box.delete("1.0", "end")
        atualizar_lista()
        messagebox.showinfo("OK", "Aula excluída.")

    # ---------------------------
    # Botões (layout limpo/centralizado)
    # ---------------------------
    frame_btn = ctk.CTkFrame(frame_form)
    frame_btn.pack(pady=10)

    btn_save_new = ctk.CTkButton(frame_btn, text="Salvar Nova Aula", width=180, command=salvar_nova_aula)
    btn_save_new.grid(row=0, column=0, padx=8, pady=6)

    btn_edit = ctk.CTkButton(frame_btn, text="Editar Aula", width=140, fg_color="orange", command=editar_aula)
    btn_edit.grid(row=0, column=1, padx=8, pady=6)

    btn_save_edit = ctk.CTkButton(frame_btn, text="Salvar Alteração", width=160, fg_color="green", command=salvar_alteracao)
    btn_save_edit.grid(row=0, column=2, padx=8, pady=6)

    btn_delete = ctk.CTkButton(frame_btn, text="Excluir Aula", width=140, fg_color="red", command=excluir_aula)
    btn_delete.grid(row=0, column=3, padx=8, pady=6)

    # atalhos: Enter no filtro aplica filtro e também é possível digitar índice e pressionar Enter
    filtro_entry.bind("<Return>", atualizar_lista)

    # Enter já ligado ao conteudo_box para salvar nova aula (veja acima)
    # também deixamos a janela responder ao Esc para fechar a modal (conveniente)
    janela.bind("<Escape>", lambda e: janela.destroy())

    # fim da função abrir_aulas
