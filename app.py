import os
import json
import shutil
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def gerar_resposta(mensagem):
    return f"Você disse: {mensagem}"


# Função decoradora para login obrigatório
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Função auxiliar para carregar usuários
def carregar_usuarios():
    try:
        with open('usuarios.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função auxiliar para salvar usuários
def salvar_usuarios(usuarios):
    with open('usuarios.json', 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4)

@app.route('/')
def pagina_login():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        usuarios = carregar_usuarios()

        if usuario in usuarios and usuarios[usuario]['senha'] == senha:
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))
        else:
            erro = 'Usuário ou senha inválidos.'
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('pagina_login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    mensagem = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        usuarios = carregar_usuarios()

        if usuario in usuarios:
            mensagem = 'Usuário já existe.'
        else:
            usuarios[usuario] = {
                'senha': senha,
                'bio': '',
                'nome': usuario,
                'frequencia': [],
                'foto': ''
            }
            salvar_usuarios(usuarios)
            return redirect(url_for('login'))
    return render_template('cadastro.html', mensagem=mensagem)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', usuario=session['usuario'])

@app.route('/inicio')
@login_required
def inicio():
    return render_template('inicio.html')

@app.route('/recompensa')
@login_required
def recompensa():
    return render_template('recompensa.html')

@app.route('/resgatar', methods=['POST'])
@login_required
def resgatar():
    codigo = "FL" + session['usuario'][:3].upper() + "2025"
    return jsonify({'codigo': codigo})

@app.route('/previsao')
@login_required
def previsao():
    return render_template('previsao.html')

@app.route('/prever', methods=['POST'])
@login_required
def prever():
    data = request.get_json()
    idade = data['idade']
    frequencia = data['frequencia']
    cancelamento = "Provável" if frequencia < 2 else "Improvável"
    return jsonify({'cancelamento': cancelamento, 'acuracia': 0.85})

@app.route('/ranking')
@login_required
def ranking():
    usuarios = carregar_usuarios()
    lista = [{'nome': u, 'pontuacao': len(usuarios[u].get('frequencia', []))} for u in usuarios]
    lista.sort(key=lambda x: x['pontuacao'], reverse=True)
    return render_template('ranking.html', ranking=lista)

@app.route('/ranking_dicas')
@login_required
def ranking_dicas():
    usuarios = carregar_usuarios()
    pontuacao = len(usuarios[session['usuario']].get('frequencia', []))
    lista = [{'nome': u, 'pontos': len(usuarios[u].get('frequencia', []))} for u in usuarios]
    lista.sort(key=lambda x: x['pontos'], reverse=True)
    return render_template('ranking_dicas.html', ranking=lista, usuario=session['usuario'], pontuacao=pontuacao)

@app.route('/progresso')
@login_required
def progresso():
    usuarios = carregar_usuarios()
    dias = [f"Dia {i+1}" for i in range(len(usuarios[session['usuario']].get('frequencia', [])))]
    frequencias = [1 for _ in dias]
    return render_template('progresso.html', dias=dias, frequencias=frequencias)


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    mensagem = data.get('mensagem')
    resposta = gerar_resposta(mensagem)
    return jsonify({'resposta': resposta})

if __name__ == '__main__':
    app.run(debug=True)
