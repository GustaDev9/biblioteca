from models.usuario import Usuario
from repositories.usuario_repository import (
    carregar_usuarios,
    gerar_proximo_id_usuario,
    salvar_usuarios,
)
from services.security_service import hash_senha, senha_esta_hashada, verificar_senha


class UsuarioService:
    def possui_contas(self) -> bool:
        return len(carregar_usuarios()) > 0

    def listar_usuarios(self) -> list[Usuario]:
        return carregar_usuarios()

    def criar_conta(self, nome: str, senha: str) -> Usuario:
        nome = nome.strip()
        senha = senha.strip()
        if not nome:
            raise ValueError("O nome do usuario nao pode ser vazio.")
        if not senha:
            raise ValueError("A senha nao pode ser vazia.")

        usuarios = carregar_usuarios()
        senha_segura = hash_senha(senha)
        novo_usuario = Usuario(
            id_usuario=gerar_proximo_id_usuario(usuarios),
            nome=nome,
            senha=senha_segura,
        )
        usuarios.append(novo_usuario)
        salvar_usuarios(usuarios)
        return novo_usuario

    def editar_conta(self, id_usuario: int, nome: str, senha: str) -> tuple[bool, str]:
        nome = nome.strip()
        senha = senha.strip()
        if not nome:
            return False, "O nome do usuario nao pode ser vazio."
        if not senha:
            return False, "A senha nao pode ser vazia."

        usuarios = carregar_usuarios()
        usuario = self._buscar_por_id(usuarios, id_usuario)
        if usuario is None:
            return False, "Usuario nao encontrado."

        usuario.nome = nome
        usuario.senha = hash_senha(senha)
        salvar_usuarios(usuarios)
        return True, "Conta atualizada com sucesso."

    def excluir_conta(self, id_usuario: int) -> tuple[bool, str]:
        usuarios = carregar_usuarios()
        usuario = self._buscar_por_id(usuarios, id_usuario)
        if usuario is None:
            return False, "Usuario nao encontrado."

        usuarios.remove(usuario)
        salvar_usuarios(usuarios)
        return True, "Conta excluida com sucesso."

    def autenticar(self, id_usuario: int, senha: str) -> tuple[bool, str, Usuario | None]:
        usuarios = carregar_usuarios()
        usuario = self._buscar_por_id(usuarios, id_usuario)
        if usuario is None:
            return False, "Usuario nao encontrado.", None

        if senha_esta_hashada(usuario.senha):
            if not verificar_senha(senha, usuario.senha):
                return False, "Senha invalida.", None
        else:
            # Migra senha legada em texto puro para hash no primeiro login valido.
            if usuario.senha != senha:
                return False, "Senha invalida.", None
            usuario.senha = hash_senha(senha)
            salvar_usuarios(usuarios)

        return True, "Acesso liberado.", usuario

    @staticmethod
    def _buscar_por_id(usuarios: list[Usuario], id_usuario: int) -> Usuario | None:
        for usuario in usuarios:
            if usuario.id == id_usuario:
                return usuario
        return None
