def ler_int(mensagem: str) -> int:
    while True:
        valor = input(mensagem).strip()
        try:
            return int(valor)
        except ValueError:
            print("Digite um numero inteiro valido.")


def ler_texto(mensagem: str) -> str:
    return input(mensagem).strip()
