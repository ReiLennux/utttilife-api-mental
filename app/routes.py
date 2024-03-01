from flask import jsonify
from app import app
from app.openai_client import chat

@app.route('/chat', methods=['POST'])
def chat_route():
    return chat()
