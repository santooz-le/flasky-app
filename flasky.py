import os
import click
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

def init_db():
    """Cria tabelas e garante que os papéis padrão existam."""
    db.create_all()

    # Garante que os papéis padrão existam
    for role_name in ['Admin', 'User']:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
    db.session.commit()

    # Atribui papel 'User' a quem ainda não tem papel
    default_role = Role.query.filter_by(name='User').first()
    sem_papel = User.query.filter_by(role_id=None).all()
    for u in sem_papel:
        u.role_id = default_role.id
    db.session.commit()

with app.app_context():
    init_db()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    app.run(debug=True)
