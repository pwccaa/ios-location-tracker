from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Banco de dados temporário (em memória)
# Estrutura: { 'id_rota': { 'pontos': [], 'status': 'active/finished', 'start': '', 'end': '' } }
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify({
        "rotas": historico_global,
        "ativa": rota_ativa_id
    })

@app.route('/location', methods=['POST'])
def update_location():
    global rota_ativa_id
    data = request.get_json()
    lat = fix_coordinate(data.get("lat"))
    lon = fix_coordinate(data.get("lon") or data.get("long"))
    
    if lat is None or lon is None:
        return jsonify({"error": "invalid"}), 400

    agora = datetime.now()
    novo_ponto = {"lat": lat, "lon": lon, "time": agora.strftime("%H:%M:%S")}

    # Lógica de criação de nova rota (Gap de 15 minutos)
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
