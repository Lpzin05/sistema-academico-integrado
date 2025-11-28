# assistente_ia.py – Assistente IA Avançado (URA + Pesquisa + Ícones + Tema Automático)

import customtkinter as ctk
import os
from PIL import Image

# ============================================
#  CONFIGURAÇÃO DE TEMA AUTOMÁTICO
# ============================================
def detectar_tema_windows():
    try:
        import winreg
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        valor, tipo = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return "light" if valor == 1 else "dark"
    except:
        return "dark"

ctk.set_appearance_mode(detectar_tema_windows())
ctk.set_default_color_theme("blue")


# ============================================
#  BASE DE CONHECIMENTO EM 2 NÍVEIS (CATEGORIA → PERGUNTA → RESPOSTA)
# ============================================

base_ura = {
    "Alunos": {
        "Como cadastrar aluno?":
            "Para cadastrar um aluno: clique em 'Cadastrar Aluno', preencha Nome, Turma e Nota e clique em Salvar.",
        "Como buscar aluno?":
            "A busca é automática! Vá em 'Buscar Aluno' e comece a digitar o nome.",
        "Como ordenar por nota?":
            "Use o botão 'Ordenar por Nota' no painel de alunos.",
        "Como gerar relatório?":
            "Clique em 'Gerar Relatório' para salvar um resumo completo em JSON."
    },

    "Turmas": {
        "Como cadastrar turma?":
            "Vá em 'Cadastrar Turma', digite o nome da turma e clique em Salvar.",
        "Onde as turmas ficam salvas?":
            "As turmas são armazenadas em data/turmas.json."
    },

    "Aulas": {
        "Como lançar aula?":
            "Em 'Gerenciar Aulas', clique em 'Nova Aula', selecione a turma e escreva o conteúdo.",
        "Como editar uma aula?":
            "Selecione a aula na lista, clique em Editar, altere o conteúdo e salve.",
        "Como excluir aula?":
            "Selecione a aula e clique em Excluir para removê-la."
    },

    "Atividades": {
        "Como enviar atividades?":
            "Vá em 'Upload/Atividades', escolha um arquivo e selecione a turma.",
        "Onde ficam armazenadas as atividades?":
            "O registro fica em data/atividades.json."
    },

    "Servidor e Rede": {
        "O que é o servidor?":
            "É o programa central que recebe dados do cliente C.",
        "O que é o cliente C?":
            "É o programa em C que envia dados ao servidor automaticamente.",
        "Como saber se o servidor está ativo?":
            "O console do servidor mostra 'Aguardando conexões...' ."
    },

    "Erros e Problemas": {
        "O sistema travou, o que fazer?":
            "Reinicie o servidor e depois reinicie o cliente.",
        "Erro 10048: Porta ocupada":
            "Significa que o servidor já está rodando. Encerre o processo no Gerenciador de Tarefas."
    }
}


# ============================================
#  FUNÇÃO PRINCIPAL DO ASSISTENTE IA
# ============================================

def abrir_assistente(app):

    janela = ctk.CTkToplevel(app)
    janela.title("Assistente IA – URA Interativa 2.0")
    janela.geometry("700x650")
    # === GARANTIR QUE A JANELA FIQUE NA FRENTE ===
    janela.lift()           # trás a janela para frente
    janela.focus_force()    # foca automaticamente
    janela.grab_set()       # trava a janela principal (modal)


    # ===========================
    # TÍTULO
    # ===========================
    ctk.CTkLabel(
        janela,
        text="🤖 Assistente Inteligente – URA Interativa",
        font=ctk.CTkFont(size=22, weight="bold")
    ).pack(pady=10)

    # ===========================
    # HISTÓRICO COM BOTÃO LIMPAR
    # ===========================
    historico = ctk.CTkTextbox(janela, width=650, height=260)
    historico.pack(pady=10)

    def limpar_historico():
        historico.delete("1.0", "end")

    ctk.CTkButton(janela, text="🧹 Limpar Histórico", width=120, command=limpar_historico).pack()

    historico.insert("end", "Olá! Escolha uma categoria abaixo ou pesquise acima.\n\n")

    # ===========================
    # CAMPO DE PESQUISA
    # ===========================
    pesquisa = ctk.CTkEntry(janela, width=400, placeholder_text="Pesquisar categorias ou perguntas...")
    pesquisa.pack(pady=10)

    # ===========================
    # FRAME DOS BOTÕES
    # ===========================
    frame_opcoes = ctk.CTkFrame(janela)
    frame_opcoes.pack(pady=10)

    # Carregar ícones
    def icon(nome):
        caminho = f"icones/{nome}.png"
        if os.path.exists(caminho):
            img = Image.open(caminho)
            img = img.resize((30, 30))
            return ctk.CTkImage(light_image=img, dark_image=img)
        return None

    icones = {
        "Alunos": icon("alunos"),
        "Turmas": icon("turmas"),
        "Aulas": icon("aulas"),
        "Atividades": icon("atividades"),
        "Servidor e Rede": icon("servidor"),
        "Erros e Problemas": icon("erro")
    }

    # ===========================
    # SUBMENU
    # ===========================
    def abrir_submenu(categoria):

        historico.insert("end", f"\n📂 Categoria selecionada: {categoria}\n\n")

        for widget in frame_opcoes.winfo_children():
            widget.destroy()

        perguntas = base_ura[categoria]

        for pergunta, resposta in perguntas.items():

            def responder(p=pergunta, r=resposta):
                historico.insert("end", f"❓ {p}\n")
                historico.insert("end", f"💬 {r}\n\n")

            ctk.CTkButton(
                frame_opcoes,
                text=f"❓ {pergunta}",
                width=550,
                command=responder
            ).pack(pady=5)

        # Botão Voltar
        ctk.CTkButton(
            frame_opcoes,
            text="⬅️ Voltar ao Menu Principal",
            fg_color="#444",
            hover_color="#333",
            command=lambda: montar_menu("")
        ).pack(pady=10)

    # ===========================
    # MENU PRINCIPAL (COM FILTRO)
    # ===========================
    def montar_menu(filtro):

        for widget in frame_opcoes.winfo_children():
            widget.destroy()

        for categoria in base_ura.keys():
            # FILTRO DA PESQUISA
            if filtro.lower() not in categoria.lower() and not any(
                filtro.lower() in pergunta.lower() for pergunta in base_ura[categoria].keys()
            ):
                continue

            ctk.CTkButton(
                frame_opcoes,
                text=f"{categoria}",
                width=550,
                height=40,
                image=icones.get(categoria),
                compound="left",
                command=lambda c=categoria: abrir_submenu(c)
            ).pack(pady=6)

    # Atualização automática da pesquisa
    def atualizar_pesquisa(event):
        montar_menu(pesquisa.get())

    pesquisa.bind("<KeyRelease>", atualizar_pesquisa)

    montar_menu("")