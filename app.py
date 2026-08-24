from flask import Flask, render_template, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'minha_chave_super_secreta_123'

DISCIPLINAS = ['DSWA5', 'DSWA4', 'DSWA3', 'DSWA2', 'DSWA1']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['nome']        = request.form.get('nome', '').strip()
        session['sobrenome']   = request.form.get('sobrenome', '').strip()
        session['instituicao'] = request.form.get('instituicao', '').strip()
        session['disciplina']  = request.form.get('disciplina', '')

    nome        = session.get('nome')
    sobrenome   = session.get('sobrenome')
    instituicao = session.get('instituicao')
    disciplina  = session.get('disciplina')

    # IP e Host da requisição
    ip_remoto = request.remote_addr
    host      = request.host

    now = datetime.now()

    return render_template(
        'index.html',
        nome=nome,
        sobrenome=sobrenome,
        instituicao=instituicao,
        disciplina=disciplina,
        ip_remoto=ip_remoto,
        host=host,
        now=now,
        disciplinas=DISCIPLINAS
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    now = datetime.now()
    return render_template('login.html', now=now)


if __name__ == '__main__':
    app.run(debug=True)
