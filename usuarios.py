# usuarios.py
# Manipulação de usuários (salva em data/usuarios.json)
import json
import os
from interface import garantir_pasta_data

CAMINHO = os.path.join(garantir_pasta_data(), "usuarios.json")

def carregar_usuarios():
    """Lê os usuários do JSON, trata arquivo inexistente ou inválido."""
    if not os.path.exists(CAMINHO):
        return []
    try:
        with open(CAMINHO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def salvar_usuarios(lista):
    """Salva lista de usuários (sobrescreve)."""
    with open(CAMINHO, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def autenticar_usuario(usuario, senha):
    """Retorna True se usuário+senha existirem."""
    usuarios = carregar_usuarios()
    for u in usuarios:
        if u.get("usuario") == usuario and u.get("senha") == senha:
            return True
    return False

def adicionar_usuario(usuario, senha):
    """Adiciona usuário se não existir; retorna True se adicionou, False se duplicado."""
    usuarios = carregar_usuarios()
    for u in usuarios:
        if u.get("usuario") == usuario:
            return False
    usuarios.append({"usuario": usuario, "senha": senha})
    salvar_usuarios(usuarios)
    return True
