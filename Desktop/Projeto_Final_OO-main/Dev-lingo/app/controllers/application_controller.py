from bottle import template, request, redirect, response
from app.models.trilha_model import TrilhaModel
from app.models.user_model import UserModel

class ApplicationController:
    #  Conecta as rotas com a lógica e os dados
    def __init__(self):
        self._trilha_model = TrilhaModel()
        self._user_model = UserModel()

    # --- Métodos para páginas públicas ---
    def index(self):
         # Exibe a página inicial do site
        return template('app/views/index.html')

    def login(self):
        # Exibe o formulário de login
        return template('app/views/login.html', error=None)

    def cadastro(self):
        # Exibe o formulário de cadastro de novos usuários
        return template('app/views/cadastro.html')

    def cursos(self):
        # Exibe a lista de cursos/trilhas disponíveis
        return template('app/views/cursos.html')

    def trilha_python(self):
        # Exibe a página visual da trilha de Python com módulos
         #Retorna todos os módulos, mas o vai filtrar o que for relevante para a trilha Python
        trilha_data = self._trilha_model.get_all_modulos()
        return template('app/views/trilha-python.html', trilha=trilha_data)

    def ver_aula(self, aula_id):
        # Exibe o conteúdo de uma aula específica
        aula, modulo = self._trilha_model.get_aula_by_id(aula_id)
        if aula:
            return template('app/views/aula_template.html', aula=aula, modulo=modulo)
        return "Aula não encontrada!"

    def ver_questao(self, questao_id):
        # Exibe uma questão específica para o aluno responder
        questao, modulo = self._trilha_model.get_questao_by_id(questao_id)
        if questao:
            return template('app/views/questao_template.html', questao=questao, modulo=modulo)
        return "Questão não encontrada!"

    def verificar_resposta(self, questao_id):
        # Processa a resposta do aluno a uma questão
        resposta_aluno = request.forms.getunicode('opcao')
        questao, _ = self._trilha_model.get_questao_by_id(questao_id)
        if not questao: return "Questão não encontrada!"
        acertou = (resposta_aluno == questao['resposta_correta'])
        return template('app/views/resultado_template.html', acertou=acertou)

    def em_construcao(self):
        # Exibe a página Em Construção
        return template('app/views/em_construcao.html')

     # --- Métodos de Autenticação de Usuário ---
    def handle_login(self):
        # Processa o envio do formulário de login
        email = request.forms.getunicode('email') 
        senha = request.forms.get('password') 
        user = self._user_model.check_credentials(email, senha) # Verifica credenciais no modelo
        if user:
             # Se login estiver certo, cria cookie de sessão e redireciona
            payload = {"email": email, "role": user['role']}
            response.set_cookie("session", payload, secret=request.app.config['bottle.secret'], path='/')
            if user['role'] == 'admin':
                return redirect('/admin/trilha')
            else:
                return redirect('/cursos')
        else:
            # Se login falhar, exibe o formulário de login com mensagem de erro.
            return template('app/views/login.html', error="Email ou senha inválidos.")

    def logout(self):
        # Desloga o usuário, apagando o cookie de sessão e redirecionando para a home
        response.delete_cookie("session", path='/')
        return redirect('/')

    # --- MÉTODOS DO PAINEL DE ADMINISTRAÇÃO  ---
    def admin_trilha_index(self):
        # Exibe a visão geral dos módulos no painel admin.
        trilha_data = self._trilha_model.get_all_modulos()
        return template('app/views/admin_trilha.html', trilha=trilha_data)

    def gerenciar_modulo(self, mod_id=None):
        if request.method == 'POST':
            # Cria ou edita um módulo.
            titulo = request.forms.getunicode('titulo')
            descricao = request.forms.getunicode('descricao')
            if mod_id:
                self._trilha_model.update_modulo(mod_id, titulo, descricao) # Atualiza existente
            else:
                self._trilha_model.create_modulo(titulo, descricao) # Cria novo
            return redirect('/admin/trilha') # Redireciona para a lista de módulos
        # Se GET, exibe o formulário
        modulo = {}
        if mod_id:
            modulo = self._trilha_model.get_modulo_by_id(mod_id) # Carrega dados para edição
        return template('app/views/form_modulo.html', modulo=modulo)

    def apagar_modulo(self, mod_id):
        # Apaga um módulo
        self._trilha_model.delete_modulo(mod_id)
        return redirect('/admin/trilha') # Redireciona de volta à lista

    def gerenciar_aula(self, mod_id, aula_id=None):
        # Cria ou edita uma aula dentro de um módulo
        modulo = self._trilha_model.get_modulo_by_id(mod_id)
        if not modulo: return "Módulo não encontrado!" # Erro se o módulo não existe
       
        if request.method == 'POST':
            titulo = request.forms.getunicode('titulo')
            conteudo = request.forms.getunicode('conteudo')
            if aula_id:
                self._trilha_model.update_aula(aula_id, titulo, conteudo) # Atualiza aula
            else:
                self._trilha_model.create_aula(mod_id, titulo, conteudo) # Cria nova aula
            return redirect(f'/admin/modulo/editar/{mod_id}') # Volta para a página de edição do módulo
        
        # Se GET, exibe o formulário
        aula = {}
        if aula_id:
            aula, _ = self._trilha_model.get_aula_by_id(aula_id) # Carrega dados da aula

        return template('app/views/form_aula.html', modulo=modulo, aula=aula)

    def apagar_aula(self, mod_id, aula_id):
        # Apaga uma aula
        self._trilha_model.delete_aula(mod_id, aula_id)
        return redirect(f'/admin/modulo/editar/{mod_id}') # Volta para a página de edição do módulo

    def gerenciar_questao(self, mod_id, questao_id=None):
        # Cria ou edita uma questão dentro de um módulo
        modulo = self._trilha_model.get_modulo_by_id(mod_id)
        if not modulo: return "Módulo não encontrado!"

        if request.method == 'POST':
            enunciado = request.forms.getunicode('enunciado')
             # Pega as opções do formulário
            opcoes = [opt for opt in [request.forms.getunicode(f'opcao_{i}') for i in range(1, 5)] if opt]
            resposta_index = int(request.forms.get('resposta_correta_index'))
            # Determina a resposta correta pelo texto da opção selecionada
            resposta_correta_texto = opcoes[resposta_index] if 0 <= resposta_index < len(opcoes) else opcoes[0]

            if questao_id:
                self._trilha_model.update_questao(questao_id, enunciado, opcoes, resposta_correta_texto) # Atualiza questão
            else:
                self._trilha_model.create_questao(mod_id, enunciado, opcoes, resposta_correta_texto) # Cria nova questão
            return redirect(f'/admin/modulo/editar/{mod_id}') # Volta para a página de edição do módulo
        # Se GET, exibe o formulário
        questao = {}
        if questao_id:
            questao, _ = self._trilha_model.get_questao_by_id(questao_id) # Carrega dados da questão
        return template('app/views/form_questao.html', modulo=modulo, questao=questao)

    def apagar_questao(self, mod_id, questao_id):
        # Apaga uma questão
        self._trilha_model.delete_questao(mod_id, questao_id)
        return redirect(f'/admin/modulo/editar/{mod_id}') # Volta para a página de edição do módulo