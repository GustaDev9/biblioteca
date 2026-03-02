from models.emprestimo import devolver, emprestar
from models.livro import Livro
from repositories.livro_repository import (
    carregar_livros,
    gerar_proximo_id,
    salvar_livros,
)


class BibliotecaService:
    def inicializar_catalogo_padrao(self) -> None:
        livros = carregar_livros()
        if livros:
            return

        livros_padrao = [
            Livro(1, "Dom Casmurro", "Machado de Assis"),
            Livro(2, "1984", "George Orwell"),
            Livro(3, "O Hobbit", "J.R.R. Tolkien"),
        ]
        salvar_livros(livros_padrao)

    def listar_livros(self) -> list[Livro]:
        return carregar_livros()

    def cadastrar_livro(self, nome: str, autor: str) -> Livro:
        nome = nome.strip()
        autor = autor.strip()

        if not nome:
            raise ValueError("O nome do livro nao pode ser vazio.")
        if not autor:
            raise ValueError("O autor do livro nao pode ser vazio.")

        livros = carregar_livros()
        novo_livro = Livro(
            id_livro=gerar_proximo_id(livros),
            nome=nome,
            autor=autor,
        )
        livros.append(novo_livro)
        salvar_livros(livros)
        return novo_livro

    def emprestar_livro(self, id_livro: int) -> tuple[bool, str]:
        livros = carregar_livros()
        livro = self._buscar_por_id(livros, id_livro)
        if livro is None:
            return False, "Livro nao encontrado."

        sucesso, mensagem = emprestar(livro)
        if sucesso:
            salvar_livros(livros)
        return sucesso, mensagem

    def devolver_livro(self, id_livro: int) -> tuple[bool, str]:
        livros = carregar_livros()
        livro = self._buscar_por_id(livros, id_livro)
        if livro is None:
            return False, "Livro nao encontrado."

        sucesso, mensagem = devolver(livro)
        if sucesso:
            salvar_livros(livros)
        return sucesso, mensagem

    @staticmethod
    def _buscar_por_id(livros: list[Livro], id_livro: int) -> Livro | None:
        for livro in livros:
            if livro.id == id_livro:
                return livro
        return None
