import os
import time
from openai import OpenAI
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

OpenAI.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

from app.utils.helpers import get_file_ids

def chat():
    data = request.json
    user_input = data.get('message')
    thread_id_geted = data.get('thread_id', None)

    file_ids = get_file_ids()

    if user_input.lower() == "quit":
        return jsonify({
            "message": "Conversación finalizada.",
            "thread_id": None
        })

    if thread_id_geted:
        my_thread = client.beta.threads.create()
        my_thread = client.beta.threads.update(
            thread_id=thread_id_geted
        )
    else:
        my_thread = client.beta.threads.create()

    my_thread_message = client.beta.threads.messages.create(
        thread_id=my_thread.id,
        role="user",
        content=user_input,
    )

    my_run = client.beta.threads.runs.create(
        thread_id=my_thread.id,
        assistant_id=os.getenv('OPENAI_ASSISTANT_ID'),
        instructions="Por favor, ayuda al usuario como si fueras un psicologo y en caso de ser necesario usa la información de los archivos adjuntos, es decir que usa la informacion de los archivos que se te suben solo en caso de que lo consideres necesario."
    )

    time.sleep(5)

    while my_run.status in ["queued", "in_progress"]:
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=my_thread.id,
            run_id=my_run.id
        )

        if keep_retrieving_run.status == "completed":
            all_messages = client.beta.threads.messages.list(
                thread_id=my_thread.id
            )

            assistant_response_text = all_messages.data[0].content[0].text.value

            break
        elif keep_retrieving_run.status in ["queued", "in_progress"]:
            time.sleep(5)
            pass
        else:
            break

    return jsonify({
        "thread_id": my_thread.id,
        "response": assistant_response_text
    })
