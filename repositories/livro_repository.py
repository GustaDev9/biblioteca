import json
from pathlib import Path

from models.livro import Livro
from services.security_service import (
    SIGNATURE_ALGORITHM,
    IntegridadeDadosError,
    assinar_payload,
    obter_chave_secreta,
    verificar_assinatura,
)

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
        raise IntegridadeDadosError(
            "Arquivo de livros corrompido: JSON invalido."
        ) from None

    if not isinstance(dados, dict):
        raise IntegridadeDadosError(
            "Arquivo de livros invalido: estrutura inesperada."
        )

    payload = {"livros": dados.get("livros", [])}
    if not isinstance(payload["livros"], list):
        raise IntegridadeDadosError(
            "Arquivo de livros invalido: campo 'livros' deve ser lista."
        )

    meta = dados.get("_meta")
    if not isinstance(meta, dict):
        raise IntegridadeDadosError(
            "Integridade comprometida: assinatura de livros ausente."
        )

    sig_alg = meta.get("sig_alg")
    assinatura = meta.get("sig")
    if sig_alg != SIGNATURE_ALGORITHM or not isinstance(assinatura, str):
        raise IntegridadeDadosError(
            "Integridade comprometida: metadados de assinatura invalidos em livros."
        )

    chave = obter_chave_secreta()
    if not verificar_assinatura(payload, assinatura, chave):
        raise IntegridadeDadosError(
            "Integridade comprometida: livros.json foi alterado manualmente."
        )

    return payload


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
    payload = {
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
    chave = obter_chave_secreta()
    assinatura = assinar_payload(payload, chave)
    dados = {
        **payload,
        "_meta": {
            "sig_alg": SIGNATURE_ALGORITHM,
            "sig": assinatura,
        },
    }
    ARQUIVO_LIVROS.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def gerar_proximo_id(livros: list[Livro]) -> int:
    if not livros:
        return 1
    return max(livro.id for livro in livros) + 1
