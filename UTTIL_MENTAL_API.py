from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import openai

# Carga las variables de entorno desde '.env'
load_dotenv()

app = Flask(__name__)

# Configura la clave API de OpenAI
openai.api_key = "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"

# ID del asistente que has creado en OpenAI
ASSISTANT_ID = "asst_pPoffznwlhg9QJ5cXRlibUHr"

@app.route('/consulta', methods=['POST'])
def consulta():
    data = request.json
    user_message = data.get('mensaje')

    if not user_message:
        return jsonify({"error": "No se proporcionó mensaje"}), 400

    try:
        # Crea un nuevo hilo
        thread = openai.Thread.create()

        # Añade el mensaje del usuario al hilo
        message = openai.Message.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # Ejecuta el asistente en el hilo
        run = openai.Run.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Espera a que el asistente complete la ejecución
        # Esta es una simplificación; en un entorno de producción, querrás manejar esto de manera asincrónica
        import time
        while run.status not in ["completed", "failed"]:
            time.sleep(1)  # Espera un segundo antes de volver a comprobar el estado
            run = openai.Run.retrieve(run.id)

        # Obtiene y muestra la respuesta del asistente
        response_messages = openai.Message.list(thread_id=thread.id)
        assistant_responses = [msg.content for msg in response_messages.data if msg.role == "assistant"]

        return jsonify({"respuestas": assistant_responses})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
