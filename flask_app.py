import os
from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'minha_chave_super_secreta_123'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

ROLES = ['Administrator', 'Moderator', 'User']


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def get_or_create_role(name):
    """Retorna a Role existente ou cria uma nova."""
    role = Role.query.filter_by(name=name).first()
    if role is None:
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
    return role


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        role_name = request.form.get('role', 'User')

        if name:
            session['name'] = name
            session['role'] = role_name

            user = User.query.filter_by(username=name).first()
            role = get_or_create_role(role_name)

            if user is None:
                user = User(username=name, role=role)
                db.session.add(user)
                session['known'] = False
            else:
                user.role = role
                session['known'] = True

            db.session.commit()

        return redirect(url_for('index'))

    name = session.get('name')
    known = session.get('known', False)
    selected_role = session.get('role', 'User')

    users = User.query.all()
    user_count = User.query.count()

    return render_template(
        'index.html',
        name=name,
        known=known,
        users=users,
        user_count=user_count,
        roles=ROLES,
        selected_role=selected_role
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        for r in ROLES:
            get_or_create_role(r)
    app.run(debug=True)
