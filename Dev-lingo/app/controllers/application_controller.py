from bottle import template, request, redirect, response
from app.models.trilha_model import TrilhaModel
from app.models.user_model import UserModel

class ApplicationController:
    # Conecta as rotas com a lógica e os dados
    def __init__(self):
        self._trilha_model = TrilhaModel()
        self._user_model = UserModel()

    # --- MÉTODOS PARA PÁGINAS PÚBLICAS ---
    # O padrão agora é: buscar a sessão e enviá-la para o template.
    
    def index(self):
        session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
        return template('app/views/index.html', session=session_data)

    def cursos(self):
        session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
        return template('app/views/cursos.html', session=session_data)
        
    def trilha_python(self):
        """ Mostra a página com a lista de todos os módulos da trilha Python. """
        trilha_data = self._trilha_model.get_all_modulos()
        # Passa os dados da sessão para o template mostrar o header correto
        session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
        return template('app/views/trilha-python.html', trilha=trilha_data, session=session_data)

    def ver_modulo(self, mod_id):
        modulo = self._trilha_model.get_modulo_by_id(mod_id)
        if not modulo: return "Módulo não encontrado!"
        session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
        progresso_data = self._user_model.get_progresso(session_data['email']) if session_data else None
        return template('app/views/modulo_detail.html', modulo=modulo, session=session_data, progresso=progresso_data)
        
    def ver_aula(self, aula_id):
        aula, modulo = self._trilha_model.get_aula_by_id(aula_id)
        if aula:
            session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
            if session_data:
                self._user_model.marcar_como_concluido(session_data['email'], 'aula', aula_id)
            return template('app/views/aula_template.html', aula=aula, modulo=modulo, session=session_data)
        return "Aula não encontrada!"

    def ver_questao(self, questao_id):
        questao, modulo = self._trilha_model.get_questao_by_id(questao_id)
        if questao:
            session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
            return template('app/views/questao_template.html', questao=questao, modulo=modulo, session=session_data)
        return "Questão não encontrada!"

    def verificar_resposta(self, questao_id):
        resposta_aluno = request.forms.getunicode('opcao')
        questao, _ = self._trilha_model.get_questao_by_id(questao_id)
        if not questao: return "Questão não encontrada!"
        
        acertou = (resposta_aluno == questao['resposta_correta'])
        
        if acertou:
            session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
            if session_data:
                self._user_model.marcar_como_concluido(session_data['email'], 'questao', questao_id)

        session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
        return template('app/views/resultado_template.html', acertou=acertou, session=session_data)
        
    def em_construcao(self):
        session_data = request.get_cookie("session", secret=request.app.config['bottle.secret'])
        return template('app/views/em_construcao.html', session=session_data)

    # --- Métodos de Autenticação de Usuário ---
    def login(self):
        # Páginas de login/cadastro não precisam mostrar info do usuário no header
        success_message = request.query.get('status') == 'success'
        return template('app/views/login.html', error=None, success=success_message)

    def cadastro(self):
        return template('app/views/cadastro.html', error=None)

    def handle_login(self):
        """ Processa o envio do formulário de login. """
        print("\n--- [DEBUG] Recebida uma tentativa de login via POST. ---")
        
        email = request.forms.getunicode('email') 
        senha = request.forms.get('password') 
        print(f"[DEBUG] Email recebido: '{email}'")
        print(f"[DEBUG] Senha recebida: '{"*"*len(senha)}'")

        print("[DEBUG] Chamando o user_model para verificar as credenciais...")
        user = self._user_model.check_credentials(email, senha)
        
        print(f"[DEBUG] Resultado da verificação (check_credentials): {user}")

        if user:
            print(f"[DEBUG] Verificação BEM-SUCEDIDA. Usuário '{user['nome']}' encontrado com role '{user['role']}'.")
            payload = {"email": email, "role": user['role']}
            response.set_cookie("session", payload, secret=request.app.config['bottle.secret'], path='/')
            
            if user['role'] == 'admin':
                print("[DEBUG] Usuário é ADMIN. Redirecionando para /admin/trilha...")
                return redirect('/admin/trilha')
            else:
                print("[DEBUG] Usuário é comum. Redirecionando para /cursos...")
                return redirect('/cursos')
        else:
            print("[DEBUG] Verificação FALHOU. Retornando para a página de login com mensagem de erro.")
            return template('app/views/login.html', error="Email ou senha inválidos.", success=False)

    def handle_cadastro(self):
        """ Processa o envio do formulário de cadastro. """
        nome = request.forms.getunicode('fullname')
        email = request.forms.getunicode('email')
        senha = request.forms.get('password')
        senha_confirm = request.forms.get('confirm-password')

        # 1. Validação: As senhas coincidem?
        if senha != senha_confirm:
            return template('app/views/cadastro.html', error="As senhas não coincidem.")
        
        # 2. Chama o model para criar o usuário
        novo_usuario = self._user_model.create_user(nome, email, senha)

        # 3. Validação: O email já estava em uso?
        if not novo_usuario:
            return template('app/views/cadastro.html', error="Este email já está em uso.")

        # 4. Se tudo deu certo, redireciona para a página de login com mensagem de sucesso
        return redirect('/login?status=success')
    
    def logout(self):
        response.delete_cookie("session", path='/')
        return redirect('/')

    # --- MÉTODOS DO PAINEL DE ADMINISTRAÇÃO ---
    def admin_trilha_index(self):
        trilha_data = self._trilha_model.get_all_modulos()
        return template('app/views/admin_trilha.html', trilha=trilha_data)
        
    def gerenciar_modulo(self, mod_id=None):
        if request.method == 'POST':
            titulo = request.forms.getunicode('titulo')
            descricao = request.forms.getunicode('descricao')
            if mod_id:
                self._trilha_model.update_modulo(mod_id, titulo, descricao)
            else:
                self._trilha_model.create_modulo(titulo, descricao)
            return redirect('/admin/trilha')
        modulo = {}
        if mod_id:
            modulo = self._trilha_model.get_modulo_by_id(mod_id)
        return template('app/views/form_modulo.html', modulo=modulo)

    def apagar_modulo(self, mod_id):
        self._trilha_model.delete_modulo(mod_id)
        return redirect('/admin/trilha')

    def gerenciar_aula(self, mod_id, aula_id=None):
        modulo = self._trilha_model.get_modulo_by_id(mod_id)
        if not modulo: return "Módulo não encontrado!"
        if request.method == 'POST':
            titulo = request.forms.getunicode('titulo')
            conteudo = request.forms.getunicode('conteudo')
            if aula_id:
                self._trilha_model.update_aula(aula_id, titulo, conteudo)
            else:
                self._trilha_model.create_aula(mod_id, titulo, conteudo)
            return redirect(f'/admin/modulo/editar/{mod_id}')
        aula = {}
        if aula_id:
            aula, _ = self._trilha_model.get_aula_by_id(aula_id)
        return template('app/views/form_aula.html', modulo=modulo, aula=aula)

    def apagar_aula(self, mod_id, aula_id):
        self._trilha_model.delete_aula(mod_id, aula_id)
        return redirect(f'/admin/modulo/editar/{mod_id}')

    def gerenciar_questao(self, mod_id, questao_id=None):
        modulo = self._trilha_model.get_modulo_by_id(mod_id)
        if not modulo: return "Módulo não encontrado!"
        if request.method == 'POST':
            enunciado = request.forms.getunicode('enunciado')
            opcoes = [opt for opt in [request.forms.getunicode(f'opcao_{i}') for i in range(1, 5)] if opt]
            resposta_index = int(request.forms.get('resposta_correta_index'))
            resposta_correta_texto = opcoes[resposta_index] if 0 <= resposta_index < len(opcoes) else opcoes[0]
            if questao_id:
                self._trilha_model.update_questao(questao_id, enunciado, opcoes, resposta_correta_texto)
            else:
                self._trilha_model.create_questao(mod_id, enunciado, opcoes, resposta_correta_texto)
            return redirect(f'/admin/modulo/editar/{mod_id}')
        questao = {}
        if questao_id:
            questao, _ = self._trilha_model.get_questao_by_id(questao_id)
        return template('app/views/form_questao.html', modulo=modulo, questao=questao)

    def apagar_questao(self, mod_id, questao_id):
        self._trilha_model.delete_questao(mod_id, questao_id)
        return redirect(f'/admin/modulo/editar/{mod_id}')
    
    def admin_users_index(self):
        """ Mostra a lista de todos os usuários registados. """
        users_data = self._user_model.get_all_users()
        return template('app/views/admin_users.html', users=users_data)

    def apagar_usuario(self, user_id):
        """ Apaga uma conta de usuário. """
        self._user_model.delete_user(user_id)
        return redirect('/admin/users')