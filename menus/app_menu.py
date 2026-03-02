from menus.biblioteca_menu import executar_menu_biblioteca
from menus.io_utils import ler_int
from menus.usuario_menu import autenticar_para_biblioteca, executar_menu_usuarios
from services.biblioteca_service import BibliotecaService
from services.bootstrap_service import inicializar_armazenamento
from services.usuario_service import UsuarioService


def executar_app() -> None:
    inicializar_armazenamento()

    biblioteca_service = BibliotecaService()
    usuario_service = UsuarioService()
    biblioteca_service.inicializar_catalogo_padrao()

    while True:
        _exibir_menu_principal()
        opcao = ler_int("Escolha uma opcao: ")

        if opcao == 1:
            executar_menu_usuarios(usuario_service)
        elif opcao == 2:
            sucesso, mensagem = autenticar_para_biblioteca(usuario_service)
            if not sucesso:
                print(mensagem)
                continue
            executar_menu_biblioteca(biblioteca_service)
        elif opcao == 0:
            print("Saindo do sistema.")
            return
        else:
            print("Opcao invalida. Tente novamente.")


def _exibir_menu_principal() -> None:
    print("\n=== Menu Principal ===")
    print("1 - Gerenciar usuarios")
    print("2 - Entrar na biblioteca")
    print("0 - Sair")
