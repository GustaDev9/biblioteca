class Livro:
    def __init__(
        self,
        id_livro: int,
        nome: str,
        autor: str,
        disponivel: bool = True,
    ):
        self.id = id_livro
        self.nome = nome
        self.autor = autor
        self.disponivel = disponivel

    def __str__(self) -> str:
        status = "Disponivel" if self.disponivel else "Emprestado"
        return f"{self.nome} - {self.autor} ({status})"
