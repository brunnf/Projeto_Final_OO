# Este model gerencia os dados dos usuários.

class UserModel:
    def __init__(self):
        # Em um app real, NUNCA guarde senhas em texto puro. Use bibliotecas
        # como passlib para gerar e verificar hashes de senhas.
        # Para nosso exemplo, faremos de forma simples.
        self.users = {
            "admin@bitlingo.com": {
                "nome": "Administrador",
                "senha": "admin123", # Apenas para este exemplo!
                "role": "admin"
            },
            "aluno@bitlingo.com": {
                "nome": "Aluno Teste",
                "senha": "aluno123",
                "role": "user"
            }
        }

    def get_user(self, email):
        """ Retorna os dados de um usuário pelo email. """
        if email in self.users:
            return self.users[email]
        return None

    def check_credentials(self, email, senha):
        """ Verifica se o email e a senha estão corretos. """
        user = self.get_user(email)
        if user and user['senha'] == senha:
            return user
        return None