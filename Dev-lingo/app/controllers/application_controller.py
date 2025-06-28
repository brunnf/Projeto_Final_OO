from bottle import template, request, redirect, response
from app.models.trilha_model import TrilhaModel
from app.models.user_model import UserModel

class ApplicationController:
    def __init__(self):
        self._trilha_model = TrilhaModel()
        self._user_model = UserModel()

    # --- Métodos para páginas públicas (sem alterações) ---
    def index(self):
        return template('app/views/index.html')
    def login(self):
        return template('app/views/login.html', error=None)
    def cadastro(self):
        return template('app/views/cadastro.html')
    def cursos(self):
        return template('app/views/cursos.html')
    def trilha_python(self):
        trilha_data = self._trilha_model.get_all_modulos()
        return template('app/views/trilha-python.html', trilha=trilha_data)
    def ver_aula(self, aula_id):
        aula, modulo = self._trilha_model.get_aula_by_id(aula_id)
        if aula:
            return template('app/views/aula_template.html', aula=aula, modulo=modulo)
        return "Aula não encontrada!"
    def ver_questao(self, questao_id):
        questao, modulo = self._trilha_model.get_questao_by_id(questao_id)
        if questao:
            return template('app/views/questao_template.html', questao=questao, modulo=modulo)
        return "Questão não encontrada!"
    def verificar_resposta(self, questao_id):
        # MUDANÇA: Usando .getunicode() para garantir a codificação correta da resposta
        resposta_aluno = request.forms.getunicode('opcao')
        questao, _ = self._trilha_model.get_questao_by_id(questao_id)
        if not questao: return "Questão não encontrada!"
        acertou = (resposta_aluno == questao['resposta_correta'])
        return template('app/views/resultado_template.html', acertou=acertou)

    def em_construcao(self):
        """ Mostra a página 'Em Construção'. """
        return template('app/views/em_construcao.html')

    # --- Métodos de Autenticação (sem alterações na lógica principal) ---
    def handle_login(self):
        email = request.forms.getunicode('email') # Usar getunicode aqui também é uma boa prática
        senha = request.forms.get('password') # Senhas geralmente não têm acentos, mas não custa
        user = self._user_model.check_credentials(email, senha)
        if user:
            payload = {"email": email, "role": user['role']}
            response.set_cookie("session", payload, secret=request.app.config['bottle.secret'], path='/')
            if user['role'] == 'admin':
                return redirect('/admin/trilha')
            else:
                return redirect('/cursos')
        else:
            return template('app/views/login.html', error="Email ou senha inválidos.")
    def logout(self):
        response.delete_cookie("session", path='/')
        return redirect('/')

    # --- MÉTODOS DO PAINEL DE ADMINISTRAÇÃO (COM CORREÇÕES) ---
    def admin_trilha_index(self):
        trilha_data = self._trilha_model.get_all_modulos()
        return template('app/views/admin_trilha.html', trilha=trilha_data)

    def gerenciar_modulo(self, mod_id=None):
        if request.method == 'POST':
            # MUDANÇA: Usando .getunicode() para garantir a codificação correta
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
            # MUDANÇA: Usando .getunicode() para garantir a codificação correta
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
            # MUDANÇA: Usando .getunicode() para garantir a codificação correta
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