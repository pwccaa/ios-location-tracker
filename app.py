from flask import Flask, request, render_template, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Agora usamos uma LISTA para guardar o histórico de todos os pontos
historico_rotas = []

def fix_coordinate(value):
    try:
        val_float = float(value)
        str_val = str(abs(int(val_float)))
        if abs(val_float) > 180:
            return val_float / (10 ** (len(str_val) - 2))
        return val_float
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Retorna a lista inteira de pontos para desenhar a linha
    return jsonify(historico_rotas)

@app.route('/location', methods=['POST'])
def update_location():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON invalido"}), 400

    raw_lat = data.get("lat")
    raw_lon = data.get("long") if data.get("long") else data.get("lon")
    
    lat = fix_coordinate(raw_lat)
    lon = fix_coordinate(raw_lon)
    
    # Só adiciona à rota se as coordenadas forem válidas
    if lat is not None and lon is not None:
        novo_ponto = {
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        historico_rotas.append(novo_ponto)
        print(f"📍 Ponto adicionado à rota: {lat}, {lon} (Total: {len(historico_rotas)})")
        return jsonify({"status": "ok", "pontos_totais": len(historico_rotas)}), 200
    else:
        return jsonify({"error": "Coordenadas invalidas"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
