class Usuario:
    def __init__(self, id_usuario: int, nome: str, senha: str):
        self.id = id_usuario
        self.nome = nome
        self.senha = senha

    def __str__(self) -> str:
        return f"{self.id} - {self.nome}"
