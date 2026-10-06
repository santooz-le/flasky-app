import os
from datetime import datetime
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
# Configuração do SendGrid
# ==============================
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', 'COLE_SUA_CHAVE_AQUI')
EMAIL_REMETENTE = 'leandrozard509@gmail.com'
EMAIL_PROFESSOR = 'flaskaulasweb@zohomail.com'
EMAIL_ALUNO = 'leandro.k@aluno.ifsp.edu.br'
PRONTUARIO = 'PT3037649'
NOME_ALUNO = 'Leandro Kauã dos Santos'


# ==============================
# Modelos
# ==============================
class Role(db.Model):
    __tablename__ = 'roles'
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id  = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    id        = db.Column(db.Integer, primary_key=True)
    de        = db.Column(db.String(128))
    para      = db.Column(db.String(256))
    assunto   = db.Column(db.String(256))
    texto     = db.Column(db.String(512))
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<EmailLog %r>' % self.assunto


# ==============================
# Helpers
# ==============================
def get_or_create_role(name):
    role = Role.query.filter_by(name=name).first()
    if role is None:
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
    return role


def enviar_email(nome_usuario, enviar_para_professor=False):
    """Envia e-mail via SendGrid API e salva no banco de dados."""
    destinatarios = [EMAIL_ALUNO]
    if enviar_para_professor:
        destinatarios.append(EMAIL_PROFESSOR)

    assunto = '[Flasky] Novo usuário'
    texto = f'Novo usuário cadastrado: {nome_usuario}'
    para_str = "',<br>'".join(destinatarios)
    para_str = f"'{para_str}'"

    try:
        response = http_requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers={
                'Authorization': f'Bearer {SENDGRID_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'personalizations': [
                    {
                        'to': [{'email': email} for email in destinatarios]
                    }
                ],
                'from': {
                    'email': EMAIL_REMETENTE,
                    'name': 'Flasky App'
                },
                'subject': assunto,
                'content': [
                    {
                        'type': 'text/html',
                        'value': f'''
                            <h2>Novo usuário cadastrado no Flasky</h2>
                            <p><strong>Prontuário:</strong> {PRONTUARIO}</p>
                            <p><strong>Nome do aluno:</strong> {NOME_ALUNO}</p>
                            <hr>
                            <p><strong>Usuário cadastrado:</strong> {nome_usuario}</p>
                        '''
                    }
                ]
            }
        )
        print(f'E-mail enviado! Status: {response.status_code} - {response.text}')

        # Salvar no banco de dados
        log = EmailLog(
            de=nome_usuario,
            para=para_str,
            assunto=assunto,
            texto=texto,
            data_hora=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        return response.status_code == 202
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
        send_email = request.form.get('send_email') == 'on'

        if name:
            session['name'] = name
            user = User.query.filter_by(username=name).first()
            if user is None:
                role = get_or_create_role('User')
                user = User(username=name, role_id=role.id)
                db.session.add(user)
                db.session.commit()
                session['known'] = False
                session['email_sent'] = enviar_email(name, enviar_para_professor=send_email)
            else:
                session['known'] = True
                session['email_sent'] = False

        return redirect(url_for('index'))

    name       = session.get('name')
    known      = session.get('known', False)
    email_sent = session.pop('email_sent', False)

    # Usuários agrupados: Administrators primeiro, depois Users
    admin_role = Role.query.filter_by(name='Administrator').first()
    user_role  = Role.query.filter_by(name='User').first()
    admins = admin_role.users.order_by(User.username).all() if admin_role else []
    users  = user_role.users.order_by(User.username).all()  if user_role  else []

    return render_template('index.html',
                           name=name,
                           known=known,
                           email_sent=email_sent,
                           admins=admins,
                           users=users)


# ==============================
# Rota de e-mails enviados
# ==============================
@app.route('/emailsEnviados')
def emails_enviados():
    emails = EmailLog.query.order_by(EmailLog.data_hora.asc()).all()
    return render_template('emails_enviados.html', emails=emails)


# ==============================
# Inicialização segura do banco
# ==============================
def init_db():
    """Cria tabelas e migra colunas faltantes sem apagar dados existentes."""
    db.create_all()

    # Adiciona role_id em users se a coluna ainda não existir (migração segura)
    with db.engine.connect() as conn:
        try:
            conn.execute(db.text('ALTER TABLE users ADD COLUMN role_id INTEGER REFERENCES roles(id)'))
            conn.commit()
        except Exception:
            pass  # coluna já existe

    # Garante que os papéis padrão existam
    get_or_create_role('Administrator')
    default_role = get_or_create_role('User')

    # Atribui papel 'User' a quem ainda não tem papel
    sem_papel = User.query.filter_by(role_id=None).all()
    for u in sem_papel:
        u.role_id = default_role.id
    db.session.commit()


with app.app_context():
    init_db()


if __name__ == '__main__':
    app.run(debug=True)
