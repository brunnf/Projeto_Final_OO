from bottle import Bottle, run, static_file, request, redirect
from functools import wraps
from app.controllers.application_controller import ApplicationController

# Cria a aplicação Bottle e o controlador principal
app = Bottle()
ctl = ApplicationController()
# Chave secreta para segurança dos cookies de sessão
app.config['bottle.secret'] = 'uma-chave-muito-secreta-e-dificil-de-adivinhar-12345'

#DECORATOR: Protege rotas para acesso exclusivo de administradores
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verifica se o usuário é admin
        user_session = request.get_cookie("session", secret=app.config['bottle.secret'])
        if user_session and user_session.get("role") == "admin":
            return fn(*args, **kwargs)
        # Redireciona para login se não for admin
        return redirect("/login") 
    return wrapper

#Rota Estática (CSS, JS, Imagens)
@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./app/static')

#Rotas Públicas
@app.route('/')
def index_route(): return ctl.index()
    
@app.route('/trilha/python')
def trilha_python_route(): return ctl.trilha_python()

@app.route('/cursos')
def cursos_route(): return ctl.cursos()

@app.route('/cadastro')
def cadastro_route(): return ctl.cadastro()

@app.route('/em-construcao')
def em_construcao_route():
    return ctl.em_construcao()

@app.route('/modulo/<mod_id:int>')
def ver_modulo_route(mod_id):
    return ctl.ver_modulo(mod_id)

#ROTAS INTERATIVAS (AULAS E QUESTÕES)

@app.route('/aula/<aula_id:int>')
def ver_aula_route(aula_id):
    return ctl.ver_aula(aula_id)

@app.route('/questao/<questao_id:int>')
def ver_questao_route(questao_id):
    return ctl.ver_questao(questao_id)

@app.route('/questao/<questao_id:int>/verificar', method='POST')
def verificar_resposta_route(questao_id):
    return ctl.verificar_resposta(questao_id)

#Rotas de Autenticação
@app.route('/login', method=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        return ctl.handle_login()
    return ctl.login()

@app.route('/logout')
def logout_route():
    return ctl.logout()

#Rotas do Admin
@app.route('/admin/trilha')
@admin_required
def admin_trilha_route():
    return ctl.admin_trilha_index()

@app.route('/admin/modulo/<mod_id:int>/aula/apagar/<aula_id:int>')
@admin_required
def apagar_aula_route(mod_id, aula_id):
    return ctl.apagar_aula(mod_id, aula_id)

@app.route('/admin/modulo/<mod_id:int>/questao/apagar/<questao_id:int>')
@admin_required
def apagar_questao_route(mod_id, questao_id):
    return ctl.apagar_questao(mod_id, questao_id)
    
@app.route('/admin/modulo/novo', method=['GET', 'POST'])
@admin_required
def criar_modulo_route():
    return ctl.gerenciar_modulo()

@app.route('/admin/modulo/editar/<mod_id:int>', method=['GET', 'POST'])
@admin_required
def editar_modulo_route(mod_id):
    return ctl.gerenciar_modulo(mod_id)

@app.route('/admin/modulo/apagar/<mod_id:int>')
@admin_required
def apagar_modulo_route(mod_id):
    return ctl.apagar_modulo(mod_id)

@app.route('/admin/modulo/<mod_id:int>/aula/novo', method=['GET', 'POST'])
@admin_required
def criar_aula_route(mod_id):
    return ctl.gerenciar_aula(mod_id)

@app.route('/admin/modulo/<mod_id:int>/questao/nova', method=['GET', 'POST'])
@admin_required
def criar_questao_route(mod_id):
    return ctl.gerenciar_questao(mod_id)

#Edição de Aulas e Questões 

@app.route('/admin/modulo/<mod_id:int>/aula/editar/<aula_id:int>', method=['GET', 'POST'])
@admin_required
def editar_aula_route(mod_id, aula_id):
    return ctl.gerenciar_aula(mod_id, aula_id)

@app.route('/admin/modulo/<mod_id:int>/questao/editar/<questao_id:int>', method=['GET', 'POST'])
@admin_required
def editar_questao_route(mod_id, questao_id):
    return ctl.gerenciar_questao(mod_id, questao_id)

@app.route('/admin/users')
@admin_required
def admin_users_route():
    return ctl.admin_users_index()

@app.route('/admin/user/apagar/<user_id:int>')
@admin_required
def apagar_usuario_route(user_id):
    return ctl.apagar_usuario(user_id)

@app.route('/cadastro', method=['GET', 'POST'])
def handle_cadastro_route():
    if request.method == 'POST':
        return ctl.handle_cadastro()
    return ctl.cadastro()

#Iniciar Servidor
if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8080, debug=True, reloader=True)