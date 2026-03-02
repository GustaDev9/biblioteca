import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
ARQUIVO_DADOS_LEGADO = STORAGE_DIR / "dados.json"
ARQUIVO_LIVROS = STORAGE_DIR / "livros.json"
ARQUIVO_USUARIOS = STORAGE_DIR / "usuarios.json"


def inicializar_armazenamento() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    dados_legado = _ler_json_dict(ARQUIVO_DADOS_LEGADO, {"livros": [], "usuarios": []})
    livros_legado = _extrair_lista(dados_legado, "livros")
    usuarios_legado = _extrair_lista(dados_legado, "usuarios")

    livros_atuais = _extrair_lista(
        _ler_json_dict(ARQUIVO_LIVROS, {"livros": []}),
        "livros",
    )
    usuarios_atuais = _extrair_lista(
        _ler_json_dict(ARQUIVO_USUARIOS, {"usuarios": []}),
        "usuarios",
    )

    if not livros_atuais and livros_legado:
        livros_atuais = livros_legado
    if not usuarios_atuais and usuarios_legado:
        usuarios_atuais = usuarios_legado

    _escrever_json(ARQUIVO_LIVROS, {"livros": livros_atuais})
    _escrever_json(ARQUIVO_USUARIOS, {"usuarios": usuarios_atuais})


def _ler_json_dict(caminho: Path, fallback: dict) -> dict:
    if not caminho.exists():
        return fallback

    conteudo = caminho.read_text(encoding="utf-8").strip()
    if not conteudo:
        return fallback

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError:
        return fallback

    if not isinstance(dados, dict):
        return fallback
    return dados


def _extrair_lista(dados: dict, chave: str) -> list:
    valor = dados.get(chave, [])
    if not isinstance(valor, list):
        return []
    return valor


def _escrever_json(caminho: Path, dados: dict) -> None:
    caminho.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
