from menus.io_utils import ler_int, ler_texto
from services.usuario_service import UsuarioService


def executar_menu_usuarios(usuario_service: UsuarioService) -> None:
    while True:
        _exibir_menu_usuarios()
        opcao = ler_int("Escolha uma opcao: ")

        if opcao == 1:
            _criar_conta(usuario_service)
        elif opcao == 2:
            _mostrar_contas(usuario_service)
        elif opcao == 3:
            _editar_conta(usuario_service)
        elif opcao == 4:
            _excluir_conta(usuario_service)
        elif opcao == 0:
            return
        else:
            print("Opcao invalida. Tente novamente.")


def autenticar_para_biblioteca(usuario_service: UsuarioService) -> tuple[bool, str]:
    if not usuario_service.possui_contas():
        return False, "Nao ha contas cadastradas. Crie uma conta primeiro."

    id_usuario = ler_int("ID do usuario: ")
    senha = ler_texto("Senha: ")
    sucesso, mensagem, usuario = usuario_service.autenticar(id_usuario, senha)

    if not sucesso or usuario is None:
        return False, mensagem

    print(f"Bem-vindo, {usuario.nome}.")
    return True, ""


def _exibir_menu_usuarios() -> None:
    print("\n=== Menu de Usuarios ===")
    print("1 - Criar conta")
    print("2 - Mostrar contas")
    print("3 - Editar conta")
    print("4 - Excluir conta")
    print("0 - Voltar")


def _criar_conta(usuario_service: UsuarioService) -> None:
    nome = ler_texto("Nome de usuario: ")
    senha = ler_texto("Senha: ")

    try:
        usuario = usuario_service.criar_conta(nome, senha)
    except ValueError as exc:
        print(f"Erro: {exc}")
        return

    print(f"Conta criada com sucesso. ID: {usuario.id}")


def _mostrar_contas(usuario_service: UsuarioService) -> None:
    usuarios = usuario_service.listar_usuarios()
    if not usuarios:
        print("Nenhuma conta cadastrada.")
        return

    print("\nContas cadastradas:")
    for usuario in usuarios:
        print(f"ID: {usuario.id} | Nome: {usuario.nome}")


def _editar_conta(usuario_service: UsuarioService) -> None:
    id_usuario = ler_int("ID da conta para editar: ")
    nome = ler_texto("Novo nome: ")
    senha = ler_texto("Nova senha: ")
    _, mensagem = usuario_service.editar_conta(id_usuario, nome, senha)
    print(mensagem)


def _excluir_conta(usuario_service: UsuarioService) -> None:
    id_usuario = ler_int("ID da conta para excluir: ")
    _, mensagem = usuario_service.excluir_conta(id_usuario)
    print(mensagem)
