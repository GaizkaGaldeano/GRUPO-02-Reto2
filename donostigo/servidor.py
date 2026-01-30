from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama # <--- Cambiamos Google por Ollama

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN
# Definimos el modelo que usará Ollama (llama3 es el más recomendado)
MODELO_IA = "llama3"

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
        
        # Con Ollama usamos el sistema de mensajes para separar instrucciones de la pregunta
        response = ollama.chat(model=MODELO_IA, messages=[
            {
                'role': 'system',
                'content': INSTRUCCIONES,
            },
            {
                'role': 'user',
                'content': pregunta,
            },
        ])
        
        respuesta_texto = response['message']['content']
        
        print(f"✅ Respuesta recibida de Ollama ({MODELO_IA})")
        return jsonify({"respuesta": respuesta_texto})

    except Exception as e:
        print(f"\n❌ ERROR EN EL SERVIDOR OLLAMA: {str(e)}\n")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Cambia 5001 por 5005 para evitar conflictos en el servidor compartido
    app.run(host='0.0.0.0', port=5005, debug=True)