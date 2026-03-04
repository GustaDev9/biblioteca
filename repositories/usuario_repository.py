import json
from pathlib import Path

from models.usuario import Usuario
from services.security_service import (
    SIGNATURE_ALGORITHM,
    IntegridadeDadosError,
    assinar_payload,
    obter_chave_secreta,
    verificar_assinatura,
)

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
        raise IntegridadeDadosError(
            "Arquivo de usuarios corrompido: JSON invalido."
        ) from None

    if not isinstance(dados, dict):
        raise IntegridadeDadosError(
            "Arquivo de usuarios invalido: estrutura inesperada."
        )

    payload = {"usuarios": dados.get("usuarios", [])}
    if not isinstance(payload["usuarios"], list):
        raise IntegridadeDadosError(
            "Arquivo de usuarios invalido: campo 'usuarios' deve ser lista."
        )

    meta = dados.get("_meta")
    if not isinstance(meta, dict):
        raise IntegridadeDadosError(
            "Integridade comprometida: assinatura de usuarios ausente."
        )

    sig_alg = meta.get("sig_alg")
    assinatura = meta.get("sig")
    if sig_alg != SIGNATURE_ALGORITHM or not isinstance(assinatura, str):
        raise IntegridadeDadosError(
            "Integridade comprometida: metadados de assinatura invalidos em usuarios."
        )

    chave = obter_chave_secreta()
    if not verificar_assinatura(payload, assinatura, chave):
        raise IntegridadeDadosError(
            "Integridade comprometida: usuarios.json foi alterado manualmente."
        )

    return payload


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
    payload = {
        "usuarios": [
            {
                "id": usuario.id,
                "nome": usuario.nome,
                "senha": usuario.senha,
            }
            for usuario in usuarios
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

    ARQUIVO_USUARIOS.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_USUARIOS.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def gerar_proximo_id_usuario(usuarios: list[Usuario]) -> int:
    if not usuarios:
        return 1
    return max(usuario.id for usuario in usuarios) + 1
