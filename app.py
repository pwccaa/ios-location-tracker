from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configurações de Segurança
app.secret_key = os.environ.get("SECRET_KEY", "super_secreta_key_123") # Necessário para usar sessões
SENHA_ACESSO = os.environ.get("SENHA_ACESSO", "admin123") # Senha da tela de login
API_KEY_IOS = os.environ.get("API_KEY", "chave_secreta_iphone") # Senha que o Atalho do iOS vai enviar

# Banco de dados temporário (em memória)
historico_global = {}
rota_ativa_id = None

def fix_coordinate(value):
    try:
        val_float = float(value)
        str_val = str(abs(int(val_float)))
        if abs(val_float) > 180:
            return val_float / (10 ** (len(str_val) - 2))
        return val_float
    except: return None

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha_digitada = request.form.get('password')
        if senha_digitada == SENHA_ACESSO:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro="Senha incorreta!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- ROTAS PROTEGIDAS DA INTERFACE ---
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/data')
def get_data():
    if not session.get('logged_in'):
        return jsonify({"error": "Não autorizado"}), 401
    return jsonify({
        "rotas": historico_global,
        "ativa": rota_ativa_id
    })

# --- ROTA DO IPHONE (Protegida por API Key) ---
@app.route('/location', methods=['POST'])
def update_location():
    global rota_ativa_id
    data = request.get_json()
    
    # Verifica se o iPhone mandou a chave certa
    if not data or data.get("key") != API_KEY_IOS:
        return jsonify({"error": "Acesso negado"}), 401

    lat = fix_coordinate(data.get("lat"))
    lon = fix_coordinate(data.get("lon") or data.get("long"))
    
    if lat is None or lon is None:
        return jsonify({"error": "invalid"}), 400

    agora = datetime.now()
    novo_ponto = {"lat": lat, "lon": lon, "time": agora.strftime("%H:%M:%S")}

    criar_nova = False
    if not rota_ativa_id:
        criar_nova = True
    else:
        ultima_rota = historico_global[rota_ativa_id]
        ultimo_ponto_time = datetime.strptime(ultima_rota['pontos'][-1]['time'], "%H:%M:%S").replace(
            year=agora.year, month=agora.month, day=agora.day)
        
        if agora - ultimo_ponto_time > timedelta(minutes=15):
            ultima_rota['status'] = 'finished'
            ultima_rota['end'] = ultima_rota['pontos'][-1]['time']
            criar_nova = True

    if criar_nova:
        rota_ativa_id = agora.strftime("%Y%m%d_%H%M%S")
        historico_global[rota_ativa_id] = {
            "id": rota_ativa_id,
            "pontos": [],
            "status": "active",
            "start": agora.strftime("%H:%M"),
            "end": "Em curso..."
        }

    historico_global[rota_ativa_id]['pontos'].append(novo_ponto)
    return jsonify({"status": "ok", "rota": rota_ativa_id}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
