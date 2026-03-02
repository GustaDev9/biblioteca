import json
from pathlib import Path

from models.usuario import Usuario

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_USUARIOS = BASE_DIR / "storage" / "usuarios.json"


def _ler_dados_usuarios() -> dict:
    if not ARQUIVO_USUARIOS.exists():
        return {"usuarios": []}

    conteudo = ARQUIVO_USUARIOS.read_text(encoding="utf-8").strip()
    if not conteudo:
        return {"usuarios": []}

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError:
        return {"usuarios": []}

    if not isinstance(dados, dict):
        return {"usuarios": []}

    dados.setdefault("usuarios", [])
    if not isinstance(dados["usuarios"], list):
        dados["usuarios"] = []
    return {"usuarios": dados["usuarios"]}


def carregar_usuarios() -> list[Usuario]:
    dados = _ler_dados_usuarios()
    usuarios: list[Usuario] = []

    for item in dados["usuarios"]:
        if not isinstance(item, dict):
            continue

        try:
            usuario = Usuario(
                id_usuario=int(item["id"]),
                nome=str(item["nome"]),
                senha=str(item["senha"]),
            )
        except (KeyError, TypeError, ValueError):
            continue

        usuarios.append(usuario)

    return usuarios


def salvar_usuarios(usuarios: list[Usuario]) -> None:
    dados = {
        "usuarios": [
            {
                "id": usuario.id,
                "nome": usuario.nome,
                "senha": usuario.senha,
            }
            for usuario in usuarios
        ]
    }

    ARQUIVO_USUARIOS.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_USUARIOS.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def gerar_proximo_id_usuario(usuarios: list[Usuario]) -> int:
    if not usuarios:
        return 1
    return max(usuario.id for usuario in usuarios) + 1
