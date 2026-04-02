from flask import Flask, request, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# Memória temporária do servidor
dados_mapa = {
    "lat": -23.5505, # Valor padrão (ex: SP)
    "lon": -46.6333,
    "timestamp": "Aguardando sinal..."
}

def fix_coordinate(value):
    try:
        val_float = float(value)
        str_val = str(abs(int(val_float)))
        if abs(val_float) > 180:
            return val_float / (10 ** (len(str_val) - 2))
        return val_float
    except:
        return 0.0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Rota que o JavaScript vai consultar para atualizar o mapa
    return jsonify(dados_mapa)

@app.route('/location', methods=['POST'])
def update_location():
    data = request.get_json()
    raw_lat = data.get("lat")
    raw_lon = data.get("long") if data.get("long") else data.get("lon")
    
    dados_mapa["lat"] = fix_coordinate(raw_lat)
    dados_mapa["lon"] = fix_coordinate(raw_lon)
    dados_mapa["timestamp"] = datetime.now().strftime("%H:%M:%S")
    
    print(f"📍 Nova localização: {dados_mapa['lat']}, {dados_mapa['lon']}")
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
