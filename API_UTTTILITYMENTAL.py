from flask import Flask, request, jsonify
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Cargar las variables de entorno desde '.env'
load_dotenv()

# Inicializar el cliente de OpenAI con tu clave API
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

# Crear la aplicación Flask
app = Flask(__name__)

@app.route('/chat', methods=['GET'])
def chat():
    data = request.json
    user_input = data.get('message')
    thread_id_geted = data.get('thread_id', None)  # Obtener el ID del thread si existe

    # Cargar los IDs de archivo desde variables de entorno
    file_ids = [os.getenv(f'OPENAI_FILE{i}_ID') for i in range(10) if os.getenv(f'OPENAI_FILE{i}_ID')]
    if user_input.lower() == "quit":
        # Aquí puedes añadir cualquier lógica de limpieza necesaria, como eliminar el thread si es necesario
        # Nota: La API de OpenAI no proporciona una manera directa de eliminar threads, por lo tanto, esta operación es simbólica
        return jsonify({
            "message": "Conversación finalizada.",
            "thread_id": None  # O considerar devolver un estado o mensaje que indique que la conversación ha terminado
        })
    if thread_id_geted:
        # Si se proporciona un thread_id, recupéralo
        my_thread = client.beta.threads.create()
        my_thread = client.beta.threads.update(
            thread_id=thread_id_geted
        )
    else:
        # Si no hay thread_id, crea un nuevo thread
        my_thread = client.beta.threads.create()

    # Añadir el mensaje del usuario al thread con los archivos adjuntos
    my_thread_message = client.beta.threads.messages.create(
        thread_id=my_thread.id,
        role="user",
        content=user_input,
        ## file_ids=file_ids
    )

    # Ejecutar el asistente en el thread
    my_run = client.beta.threads.runs.create(
        thread_id=my_thread.id,
        assistant_id=os.getenv('OPENAI_ASSISTANT_ID'),
        instructions="Por favor, ayuda al usuario como si fueras un psicologo y en caso de ser necesario usa la información de los archivos adjuntos, es decir que usa la informacion de los archivos que se te suben solo en caso de que lo consideres necesario."
    )

    # Esperar de manera activa a que el asistente responda
    # Initial delay before the first retrieval
    time.sleep(5)

    # Periodically retrieve the run to check its status
    while my_run.status in ["queued", "in_progress"]:
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=my_thread.id,
            run_id=my_run.id
        )

        if keep_retrieving_run.status == "completed":
            # Retrieve the messages added by the assistant to the thread
            all_messages = client.beta.threads.messages.list(
                thread_id=my_thread.id
            )

            # Display assistant message
            assistant_response_text = all_messages.data[0].content[0].text.value

            break
        elif keep_retrieving_run.status in ["queued", "in_progress"]:
            # Delay before the next retrieval attempt
            time.sleep(5)
            pass
        else:
            break

    return jsonify({
        "thread_id": my_thread.id,  # Devolver el ID del thread para mantener el estado
        "response": assistant_response_text  # La respuesta del asistente como texto
    })


if __name__ == '__main__':
    app.run(debug=True)
