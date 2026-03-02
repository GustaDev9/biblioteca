import json
from pathlib import Path

from models.livro import Livro

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_LIVROS = BASE_DIR / "storage" / "livros.json"


def _ler_dados_livros() -> dict:
    if not ARQUIVO_LIVROS.exists():
        return {"livros": []}

    conteudo = ARQUIVO_LIVROS.read_text(encoding="utf-8").strip()
    if not conteudo:
        return {"livros": []}

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError:
        return {"livros": []}

    if not isinstance(dados, dict):
        return {"livros": []}

    dados.setdefault("livros", [])
    if not isinstance(dados["livros"], list):
        dados["livros"] = []
    return {"livros": dados["livros"]}


def carregar_livros() -> list[Livro]:
    dados = _ler_dados_livros()
    livros: list[Livro] = []

    for item in dados["livros"]:
        if not isinstance(item, dict):
            continue

        try:
            livro = Livro(
                id_livro=int(item["id"]),
                nome=str(item["nome"]),
                autor=str(item["autor"]),
                disponivel=bool(item.get("disponivel", True)),
            )
        except (KeyError, TypeError, ValueError):
            continue

        livros.append(livro)

    return livros


def salvar_livros(livros: list[Livro]) -> None:
    ARQUIVO_LIVROS.parent.mkdir(parents=True, exist_ok=True)
    dados = {
        "livros": [
            {
                "id": livro.id,
                "nome": livro.nome,
                "autor": livro.autor,
                "disponivel": livro.disponivel,
            }
            for livro in livros
        ]
    }
    ARQUIVO_LIVROS.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def gerar_proximo_id(livros: list[Livro]) -> int:
    if not livros:
        return 1
    return max(livro.id for livro in livros) + 1
