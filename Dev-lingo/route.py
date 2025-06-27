# Importando as funções necessárias do Bottle
from bottle import Bottle, run, static_file, template

# Cria a instância da aplicação
app = Bottle()

#-----------------------------------------------------------------------------
# Rota para servir arquivos estáticos (CSS, JS, Imagens)
# Esta rota é essencial para que o CSS e o JS funcionem.
@app.route('/static/<filepath:path>')
def serve_static(filepath):
    # O root aponta para a pasta 'app/static' a partir de onde o script é executado
    return static_file(filepath, root='./app/static')


#-----------------------------------------------------------------------------
# Rotas para cada uma das nossas páginas (Views)

@app.route('/')
def index():
    """ Rota para a página inicial (homepage). """
    return template('app/views/index.html')

@app.route('/login')
def login():
    """ Rota para a página de login. """
    return template('app/views/login.html')

@app.route('/cadastro')
def cadastro():
    """ Rota para a página de cadastro. """
    return template('app/views/cadastro.html')

@app.route('/cursos')
def cursos():
    """ Rota para a página de seleção de cursos. """
    return template('app/views/cursos.html')

@app.route('/trilha/python')
def trilha_python():
    """ Rota para a trilha de aprendizado de Python. """
    return template('app/views/trilha-python.html')


#-----------------------------------------------------------------------------
# Bloco para iniciar o servidor

if __name__ == '__main__':
    # Roda a aplicação. O debug=True ajuda a ver os erros e recarrega o servidor automaticamente.
    run(app, host='0.0.0.0', port=8080, debug=True, reloader=True)