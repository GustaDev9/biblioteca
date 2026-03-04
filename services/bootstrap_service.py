import json
from pathlib import Path

from services.security_service import (
    SIGNATURE_ALGORITHM,
    IntegridadeDadosError,
    assinar_payload,
    obter_chave_secreta,
    verificar_assinatura,
)

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
ARQUIVO_DADOS_LEGADO = STORAGE_DIR / "dados.json"
ARQUIVO_LIVROS = STORAGE_DIR / "livros.json"
ARQUIVO_USUARIOS = STORAGE_DIR / "usuarios.json"


def inicializar_armazenamento() -> None:
    chave = obter_chave_secreta()
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    dados_legado = _ler_json_dict(ARQUIVO_DADOS_LEGADO, {"livros": [], "usuarios": []})
    livros_legado = _extrair_lista(dados_legado, "livros")
    usuarios_legado = _extrair_lista(dados_legado, "usuarios")

    _garantir_arquivo_assinado(
        caminho=ARQUIVO_LIVROS,
        chave_payload="livros",
        dados_legado=livros_legado,
        chave_secreta=chave,
    )
    _garantir_arquivo_assinado(
        caminho=ARQUIVO_USUARIOS,
        chave_payload="usuarios",
        dados_legado=usuarios_legado,
        chave_secreta=chave,
    )


def _ler_json_dict(caminho: Path, fallback: dict, strict: bool = False) -> dict:
    if not caminho.exists():
        return fallback

    conteudo = caminho.read_text(encoding="utf-8").strip()
    if not conteudo:
        return fallback

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError:
        if strict:
            raise IntegridadeDadosError(
                f"Arquivo {caminho.name} corrompido: JSON invalido."
            ) from None
        return fallback

    if not isinstance(dados, dict):
        if strict:
            raise IntegridadeDadosError(
                f"Arquivo {caminho.name} invalido: estrutura inesperada."
            )
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


def _garantir_arquivo_assinado(
    caminho: Path,
    chave_payload: str,
    dados_legado: list,
    chave_secreta: bytes,
) -> None:
    dados_arquivo = _ler_json_dict(caminho, {}, strict=True)
    lista_legada = dados_legado if isinstance(dados_legado, list) else []

    if not caminho.exists() or _arquivo_vazio(caminho):
        payload = {chave_payload: lista_legada}
        _escrever_assinado(caminho, payload, chave_secreta)
        return

    if not isinstance(dados_arquivo, dict):
        raise IntegridadeDadosError(f"Estrutura invalida em {caminho.name}.")

    payload = {chave_payload: dados_arquivo.get(chave_payload, [])}
    if not isinstance(payload[chave_payload], list):
        raise IntegridadeDadosError(
            f"Estrutura invalida em {caminho.name}: campo '{chave_payload}' nao e lista."
        )

    meta = dados_arquivo.get("_meta")
    if not isinstance(meta, dict):
        # Arquivo legado sem assinatura: assina mantendo o conteudo atual.
        _escrever_assinado(caminho, payload, chave_secreta)
        return

    assinatura = meta.get("sig")
    sig_alg = meta.get("sig_alg")
    if sig_alg != SIGNATURE_ALGORITHM or not isinstance(assinatura, str):
        raise IntegridadeDadosError(
            f"Metadados de assinatura invalidos em {caminho.name}."
        )

    if not verificar_assinatura(payload, assinatura, chave_secreta):
        raise IntegridadeDadosError(
            f"Integridade comprometida: {caminho.name} foi alterado manualmente."
        )


def _escrever_assinado(caminho: Path, payload: dict, chave_secreta: bytes) -> None:
    assinatura = assinar_payload(payload, chave_secreta)
    dados = {
        **payload,
        "_meta": {
            "sig_alg": SIGNATURE_ALGORITHM,
            "sig": assinatura,
        },
    }
    _escrever_json(caminho, dados)


def _arquivo_vazio(caminho: Path) -> bool:
    if not caminho.exists():
        return True
    return caminho.read_text(encoding="utf-8").strip() == ""
