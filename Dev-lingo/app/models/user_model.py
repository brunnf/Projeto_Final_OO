
class UserModel:
    def __init__(self):
        # Usuários fixos para exemplo.
        self.users = {
            "admin@bitlingo.com": { 
                "nome": "Administrador",  # Usuário para mostrar o funcionamento do CRUD
                "senha": "admin123", 
                "role": "admin"
            },
            "aluno@bitlingo.com": {
                "nome": "Aluno Teste",     #Usuário para mostrar o funcionamento da parte aluno
                "senha": "aluno123",
                "role": "user"
            }
        }

    def get_user(self, email):
        # Retorna os dados de um usuário pelo email.
        if email in self.users:
            return self.users[email]
        return None

    def check_credentials(self, email, senha):
        # Verifica se email e senha estão corretos.
        user = self.get_user(email)
        if user and user['senha'] == senha:
            return user
        return None