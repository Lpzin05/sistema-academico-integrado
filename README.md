# 🎓 Sistema Acadêmico Integrado – Python + TCP + C

Projeto final desenvolvido para demonstrar integração completa entre:

- Interface gráfica com **Python (CustomTkinter)**
- Arquitetura **Cliente/Servidor TCP**
- Módulo cliente em **Linguagem C (Winsock)**
- Persistência de dados em **JSON**
- Upload de arquivos
- CRUD de alunos, turmas, aulas e atividades
- Assistente IA interno estilo URA

Este sistema foi criado do zero para simular um ambiente acadêmico com múltiplos módulos, comunicação em rede e organização profissional.

---

## 🧩 Funcionalidades do Sistema

### 🟦 Alunos
- Cadastrar aluno (Nome, Turma, Nota)
- Busca em tempo real
- Ordenação por notas (maior → menor)
- Geração de **PDF** completo com tabela e estatísticas

### 🟩 Turmas
- Cadastro completo de turmas
- Organização por professor e turno

### 🟧 Aulas
- Criar, editar e excluir aulas
- Filtro por turma
- Filtro por texto ou índice
- Salvamento automático em JSON

### 🟪 Atividades (Upload)
- Upload de PDF, imagem, DOCX, ZIP e outros arquivos
- Registro da atividade em JSON
- Organização por turma

### 🤖 Assistente IA (URA 2.0)
- Perguntas e respostas rápidas sobre o sistema
- Pesquisa por categorias
- Ícones personalizados
- Janela modal totalmente integrada à GUI

---

## 🖥️ Servidor TCP (Python)
O arquivo `servidor.py` é um **servidor TCP multi-clientes** que:

- Recebe dados enviados pelo cliente C
- Lida com concorrência via threads
- Grava os dados de forma **atômica** em JSON
- Aceita conexões LAN (0.0.0.0:5050)
- Envia resposta “OK” ao cliente

Inicie com:

```bash
python servidor.py
