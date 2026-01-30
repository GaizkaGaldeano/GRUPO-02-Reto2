from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN
# Quitamos las http_options para que Google elija la mejor ruta solo
client = genai.Client(api_key="AIzaSyCk0oEZu080r6UvrjHzej_ht16dDLhfrJU")

INSTRUCCIONES = """Eres el asistente de Taxis Donostia. 
Paradas: Avenida 45, Avenida Madrid 9, Virgen del Carmen 11, Jose María Salaberria, 
Estornes-Igara, Trento-Ondarreta, Easo Pza, Autobus Geltokia, Iparraldeko Geltokia, 
Idiakez, Manterola, Satrustegi, Nafarroa Hiribidea, Aranzazu Ospitalea, Boulevard 25, 
Colón Ibilbidea 11, Aita Larroka, Toribio Alzaga, Izaburu kalea y Julio Urkixo. 
Precios: Aeropuerto San Sebastián (20€), Aeropuerto Bilbao (35€), Aeropuerto Vitoria (30€), 
Estación Tren (15€), Puerto Pasajes (18€). Otros: Bilbao (100€), Biarritz (70€)."""

@app.route('/chat', methods=['POST'])
def chat():
    try:
        datos = request.json
        pregunta = datos.get("pregunta")
        
        if not pregunta:
            return jsonify({"error": "No hay mensaje"}), 400

        print(f"👤 Usuario pregunta: {pregunta}")
        
        # PROBAMOS CON EL NOMBRE DE MODELO MÁS COMPATIBLE
        prompt_completo = f"{INSTRUCCIONES}\n\nPregunta del cliente: {pregunta}"

        response = client.models.generate_content(
            model="gemini-1.5-flash-001", # <--- Este nombre es específico y suele saltarse el error 404
            contents=prompt_completo
        )
        
        print(f"✅ Respuesta recibida de Google")
        return jsonify({"respuesta": response.text})

    except Exception as e:
        print(f"\n❌ ERROR EN EL SERVIDOR: {str(e)}\n")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)