import json

class UserModel:
    def __init__(self, db_path='app/dados/users.json'):
        self.db_path = db_path

    def _ler_dados(self):
        """Lê todo o conteúdo do arquivo JSON e o retorna."""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existir ou estiver vazio/corrompido, retorna uma estrutura padrão
            return {"proximo_id_usuario": 1, "usuarios": []}

    def _salvar_dados(self, dados):
        """Recebe um dicionário de dados e o salva no arquivo JSON."""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def get_user_by_email(self, email):
        """ Retorna os dados de um usuário pelo email. """
        dados = self._ler_dados()
        return next((u for u in dados.get('usuarios', []) if u['email'] == email), None)

    def check_credentials(self, email, senha):
        """ Verifica as credenciais com uma simples comparação de texto. """
        user = self.get_user_by_email(email)
        if user and user.get('senha') == senha:
            return user
        return None

    def create_user(self, nome, email, senha):
        """ Cria um novo usuário e salva no ficheiro JSON. """
        if self.get_user_by_email(email):
            return None # Utilizador já existe

        dados = self._ler_dados()
        
        novo_usuario = {
            "id": dados.get('proximo_id_usuario', 1),
            "nome": nome,
            "email": email,
            "senha": senha,
            "role": "user",
            "progresso": {"aulas_concluidas": [], "questoes_concluidas": []}
        }
        
        dados.setdefault('usuarios', []).append(novo_usuario)
        dados['proximo_id_usuario'] = dados.get('proximo_id_usuario', 1) + 1
        
        self._salvar_dados(dados)
        return novo_usuario

    def get_all_users(self):
        """ Retorna a lista de todos os usuários. """
        dados = self._ler_dados()
        return dados.get('usuarios', [])

    def delete_user(self, user_id):
        """ Apaga um usuário pelo seu ID, protegendo o admin principal. """
        if user_id == 1: # Proteção para não apagar o admin principal
            return False
            
        dados = self._ler_dados()
        usuarios = dados.get('usuarios', [])
        initial_len = len(usuarios)
        
        # Cria uma nova lista sem o usuário a ser deletado
        dados['usuarios'] = [u for u in usuarios if u.get('id') != user_id]
        
        if len(dados['usuarios']) < initial_len:
            self._salvar_dados(dados)
            return True
        return False

    # --- MÉTODOS DE PROGRESSÃO ---
    
    def get_progresso(self, email):
        """ Retorna o dicionário de progresso de um usuário. """
        user = self.get_user_by_email(email)
        if not user: 
            return {'aulas_concluidas': [], 'questoes_concluidas': []}
        # Garante que a chave 'progresso' exista no usuário
        return user.setdefault('progresso', {'aulas_concluidas': [], 'questoes_concluidas': []})

    def marcar_como_concluido(self, email, tipo, item_id):
        """ Marca uma aula ou questão como concluída para um usuário. """
        dados = self._ler_dados()
        # Encontra o usuário na lista de dados lida do ficheiro
        user = next((u for u in dados.get('usuarios', []) if u.get('email') == email), None)
        
        if not user: 
            return False

        # Garante que a sub-estrutura de progresso exista corretamente
        progresso = user.setdefault('progresso', {'aulas_concluidas': [], 'questoes_concluidas': []})
        chave = f'{tipo}s_concluidas'
        lista_concluidos = progresso.setdefault(chave, [])

        if item_id not in lista_concluidos:
            lista_concluidos.append(item_id)
            self._salvar_dados(dados) # Salva a estrutura de dados completa e modificada
            return True
        return False # Retorna False se o item já estava na lista