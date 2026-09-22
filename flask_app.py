import os
import requests as http_requests
from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'minha_chave_super_secreta_123'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================
# Configuração do Resend
# ==============================
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', 'COLE_SUA_CHAVE_AQUI')

EMAIL_DESTINATARIOS = [
    'flaskaulasweb@zohomail.com',
    'leandro.k@aluno.ifsp.edu.br'
]

PRONTUARIO = 'PT3037649'
NOME_ALUNO = 'Leandro Kauã dos Santos'


# ==============================
# Modelo
# ==============================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<User %r>' % self.username


# ==============================
# Função de envio de e-mail
# ==============================
def enviar_email(nome_usuario):
    """Envia e-mail via Resend API para o professor e para o aluno."""
    try:
        response = http_requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'from': 'Flasky App <onboarding@resend.dev>',
                'to': EMAIL_DESTINATARIOS,
                'subject': f'Novo usuário cadastrado - {nome_usuario}',
                'html': f'''
                    <h2>Novo usuário cadastrado no Flasky</h2>
                    <p><strong>Prontuário:</strong> {PRONTUARIO}</p>
                    <p><strong>Nome do aluno:</strong> {NOME_ALUNO}</p>
                    <hr>
                    <p><strong>Usuário cadastrado:</strong> {nome_usuario}</p>
                '''
            }
        )
        print(f'E-mail enviado! Status: {response.status_code} - {response.text}')
        return response.status_code == 200
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')
        return False


# ==============================
# Rota principal
# ==============================
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            session['name'] = name
            user = User.query.filter_by(username=name).first()
            if user is None:
                # Novo usuário — salva e envia e-mail
                user = User(username=name)
                db.session.add(user)
                db.session.commit()
                session['known'] = False
                enviar_email(name)
            else:
                session['known'] = True
        return redirect(url_for('index'))

    name = session.get('name')
    known = session.get('known', False)
    return render_template('index.html', name=name, known=known)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
