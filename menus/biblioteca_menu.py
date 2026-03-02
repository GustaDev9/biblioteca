from menus.io_utils import ler_int, ler_texto
from services.biblioteca_service import BibliotecaService


def executar_menu_biblioteca(biblioteca_service: BibliotecaService) -> None:
    while True:
        _exibir_menu_biblioteca()
        opcao = ler_int("Escolha uma opcao: ")

        if opcao == 1:
            _listar_livros(biblioteca_service)
        elif opcao == 2:
            _cadastrar_livro(biblioteca_service)
        elif opcao == 3:
            _emprestar_livro(biblioteca_service)
        elif opcao == 4:
            _devolver_livro(biblioteca_service)
        elif opcao == 0:
            return
        else:
            print("Opcao invalida. Tente novamente.")


def _exibir_menu_biblioteca() -> None:
    print("\n=== Biblioteca ===")
    print("1 - Listar livros")
    print("2 - Cadastrar livro")
    print("3 - Emprestar livro por ID")
    print("4 - Devolver livro por ID")
    print("0 - Voltar")


def _listar_livros(service: BibliotecaService) -> None:
    livros = service.listar_livros()
    if not livros:
        print("Nenhum livro cadastrado.")
        return

    print("\nCatalogo:")
    for livro in livros:
        status = "Disponivel" if livro.disponivel else "Emprestado"
        print(f"ID: {livro.id} | Nome: {livro.nome} | Autor: {livro.autor} | {status}")


def _cadastrar_livro(service: BibliotecaService) -> None:
    nome = ler_texto("Nome do livro: ")
    autor = ler_texto("Autor do livro: ")

    try:
        livro = service.cadastrar_livro(nome, autor)
    except ValueError as exc:
        print(f"Erro: {exc}")
        return

    print(f"Livro cadastrado com sucesso. ID: {livro.id}")


def _emprestar_livro(service: BibliotecaService) -> None:
    id_livro = ler_int("ID do livro para emprestimo: ")
    _, mensagem = service.emprestar_livro(id_livro)
    print(mensagem)


def _devolver_livro(service: BibliotecaService) -> None:
    id_livro = ler_int("ID do livro para devolucao: ")
    _, mensagem = service.devolver_livro(id_livro)
    print(mensagem)
