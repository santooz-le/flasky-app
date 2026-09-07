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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            session['name'] = name
            user = User.query.filter_by(username=name).first()
            if user is None:
                # Se for novo, associa à função User
                user_role = Role.query.filter_by(name='User').first()
                if user_role is None:
                    user_role = Role(name='User')
                    db.session.add(user_role)
                    db.session.commit()
                
                user = User(username=name, role=user_role)
                db.session.add(user)
                db.session.commit()
                session['known'] = False
            else:
                session['known'] = True
        return redirect(url_for('index'))

    name = session.get('name')
    known = session.get('known', False)
    users = User.query.all()
    return render_template('index.html', name=name, known=known, users=users)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Garante que as funções Administrator e User existam
        if Role.query.filter_by(name='Administrator').first() is None:
            db.session.add(Role(name='Administrator'))
        if Role.query.filter_by(name='User').first() is None:
            db.session.add(Role(name='User'))
        db.session.commit()
    app.run(debug=True)
