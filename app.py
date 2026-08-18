from flask import Flask, render_template, request, session

app = Flask(__name__)

# Chave secreta obrigatória para usar sessions
app.secret_key = 'minha_chave_super_secreta_123'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Salva o nome na sessão do usuário
        session['name'] = request.form.get('name')

    # Pega o nome da sessão (se existir)
    name = session.get('name')
    return render_template('index.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
