from models.livro import Livro


def emprestar(livro: Livro) -> tuple[bool, str]:
    if not livro.disponivel:
        return False, "Esse livro ja esta emprestado."

    livro.disponivel = False
    return True, "Livro emprestado com sucesso."


def devolver(livro: Livro) -> tuple[bool, str]:
    if livro.disponivel:
        return False, "Esse livro ja esta disponivel."

    livro.disponivel = True
    return True, "Livro devolvido com sucesso."
