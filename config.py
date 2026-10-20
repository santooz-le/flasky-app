import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'minha_chave_super_secreta_123'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <leandrozard509@gmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN', 'flaskaulasweb@zohomail.com')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SendGrid & dados do aluno
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', 'COLE_SUA_CHAVE_AQUI')
    EMAIL_REMETENTE = 'leandrozard509@gmail.com'
    EMAIL_PROFESSOR = 'flaskaulasweb@zohomail.com'
    EMAIL_ALUNO = 'leandro.k@aluno.ifsp.edu.br'
    PRONTUARIO = 'PT3037649'
    NOME_ALUNO = 'Leandro Kauã dos Santos'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
