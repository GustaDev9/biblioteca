import base64
import hashlib
import hmac
import json
import os

ENV_SECRET_KEY = "BIBLIOTECA_SECRET_KEY"
PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 600_000
PBKDF2_PREFIX = "pbkdf2_sha256"
SIGNATURE_ALGORITHM = "hmac_sha256"


class IntegridadeDadosError(Exception):
    pass


class ConfiguracaoSegurancaError(Exception):
    pass


def obter_chave_secreta() -> bytes:
    valor = os.getenv(ENV_SECRET_KEY, "").strip()
    if not valor:
        raise ConfiguracaoSegurancaError(
            f"Defina a variavel de ambiente {ENV_SECRET_KEY} para iniciar o sistema."
        )

    chave = valor.encode("utf-8")
    if len(chave) < 16:
        raise ConfiguracaoSegurancaError(
            f"A variavel {ENV_SECRET_KEY} precisa ter ao menos 16 caracteres."
        )
    return chave


def senha_esta_hashada(valor: str) -> bool:
    if not isinstance(valor, str):
        return False

    partes = valor.split("$")
    if len(partes) != 4:
        return False
    if partes[0] != PBKDF2_PREFIX:
        return False

    iteracoes = partes[1]
    return iteracoes.isdigit()


def hash_senha(senha: str) -> str:
    salt = os.urandom(16)
    senha_hash = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        senha.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(senha_hash).decode("ascii")
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt_b64}${hash_b64}"


def verificar_senha(senha_plana: str, senha_armazenada: str) -> bool:
    if not senha_esta_hashada(senha_armazenada):
        return False

    try:
        prefixo, iteracoes_str, salt_b64, hash_b64 = senha_armazenada.split("$")
        if prefixo != PBKDF2_PREFIX:
            return False

        iteracoes = int(iteracoes_str)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        hash_original = base64.b64decode(hash_b64.encode("ascii"))
    except (ValueError, TypeError):
        return False

    hash_teste = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        senha_plana.encode("utf-8"),
        salt,
        iteracoes,
    )
    return hmac.compare_digest(hash_teste, hash_original)


def assinar_payload(payload: dict, chave: bytes) -> str:
    mensagem = _serializar_payload(payload)
    assinatura = hmac.new(chave, mensagem, hashlib.sha256).hexdigest()
    return assinatura


def verificar_assinatura(payload: dict, assinatura: str, chave: bytes) -> bool:
    assinatura_esperada = assinar_payload(payload, chave)
    return hmac.compare_digest(assinatura_esperada, assinatura)


def _serializar_payload(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
