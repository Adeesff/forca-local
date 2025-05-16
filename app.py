import os
import json
import shutil
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from functools import wraps
from werkzeug.utils import secure_filename

from utils import responder_chatbot

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    usuarios = carregar_usuarios()
    usuario = session['usuario']
    if request.method == 'POST':
        usuarios[usuario]['nome'] = request.form['nome']
        usuarios[usuario]['bio'] = request.form['bio']
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                filename = secure_filename(foto.filename)
                caminho = os.path.join(UPLOAD_FOLDER, filename)
                foto.save(caminho)
                usuarios[usuario]['foto'] = caminho
        salvar_usuarios(usuarios)
    return render_template('perfil.html', usuario=usuario, dados=usuarios[usuario])

@app.route('/perfil/<nome_usuario>')
@login_required
def visualizar_perfil(nome_usuario):
    usuarios = carregar_usuarios()
    if nome_usuario in usuarios:
        return render_template('visualizar_perfil.html', usuario=nome_usuario, dados=usuarios[nome_usuario])
    return "Usuário não encontrado", 404

@app.route('/chat')
@login_required
def chat():
    usuarios = carregar_usuarios()
    return render_template('chat.html', usuarios=usuarios.keys())

@app.route('/backup')
@login_required
def backup():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta_backup = f"backup_{agora}"
    os.makedirs(pasta_backup, exist_ok=True)
    shutil.copy("usuarios.json", os.path.join(pasta_backup, "usuarios.json"))
    shutil.make_archive(pasta_backup, 'zip', pasta_backup)
    shutil.rmtree(pasta_backup)
    return send_file(f"{pasta_backup}.zip", as_attachment=True)

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat_view():
    usuario = session['usuario']
    if request.method == 'POST':
        mensagem = request.form['mensagem']
        mensagem.append({'remetente': usuario, 'mensagem': mensagem})
    return render_template('chat.html', mensagens=mensagem)




if __name__ == '__main__':
    app.run(debug=True)
