import requests as http_requests
from flask import current_app

def send_email(username, extra_email=None):
    """Envia notificação por e-mail via SendGrid API.
    
    Destinatários fixos:
      - flaskaulasweb@zohomail.com (professor)
      - leandro.k@aluno.ifsp.edu.br (aluno institucional)
    Destinatário opcional:
      - extra_email (informado pelo usuário no formulário)
    """
    api_key = current_app.config.get('SENDGRID_API_KEY')
    remetente = current_app.config.get('EMAIL_REMETENTE', 'leandrozard509@gmail.com')
    destinatarios = [
        current_app.config.get('EMAIL_PROFESSOR', 'flaskaulasweb@zohomail.com'),
        current_app.config.get('EMAIL_ALUNO', 'leandro.k@aluno.ifsp.edu.br')
    ]

    # Adiciona o e-mail informado no formulário, se houver
    if extra_email and extra_email not in destinatarios:
        destinatarios.append(extra_email)

    prontuario = current_app.config.get('PRONTUARIO', 'PT3037649')
    nome_aluno = current_app.config.get('NOME_ALUNO', 'Leandro Kauã dos Santos')

    assunto = f"{current_app.config.get('FLASKY_MAIL_SUBJECT_PREFIX', '[Flasky]')} Novo usuário"
    conteudo_html = f"""
        <h2>Novo usuário cadastrado no Flasky</h2>
        <p><strong>Prontuário:</strong> {prontuario}</p>
        <p><strong>Nome do aluno:</strong> {nome_aluno}</p>
        <hr>
        <p><strong>Usuário cadastrado:</strong> {username}</p>
    """

    try:
        response = http_requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'personalizations': [
                    {
                        'to': [{'email': email} for email in destinatarios]
                    }
                ],
                'from': {
                    'email': remetente,
                    'name': 'Flasky App'
                },
                'subject': assunto,
                'content': [
                    {
                        'type': 'text/html',
                        'value': conteudo_html
                    }
                ]
            },
            timeout=10
        )
        print(f"E-mail enviado! Status: {response.status_code}")
        return response.status_code == 202
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False
