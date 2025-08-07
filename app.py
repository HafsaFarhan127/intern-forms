from flask import Flask, request, jsonify, render_template, session
from utils.chat_storage import ChatStorage
from query_testing import LLM_responds
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
chat_storage = ChatStorage()

@app.route('/')
def index():
    if 'chat_id' not in session:
        session['chat_id'] = chat_storage.create_new_chat()
    
    chat_history = chat_storage.get_chat_history(session['chat_id'])
    all_chats = chat_storage.get_all_chats()
    return render_template('chat.html', 
                         chat_history=chat_history, 
                         all_chats=all_chats,
                         current_chat_id=session['chat_id'])

@app.route('/new_chat')
def new_chat():
    session['chat_id'] = chat_storage.create_new_chat()
    return jsonify({'chat_id': session['chat_id']})

@app.route('/chat/<chat_id>')
def load_chat(chat_id):
    session['chat_id'] = chat_id
    chat_history = chat_storage.get_chat_history(chat_id)
    return jsonify({'history': chat_history})

@app.route('/query', methods=['POST'])
def query():
    try:
        user_query = request.json.get('query')
        response = LLM_responds(user_query)
        
        chat_storage.save_message(
            session['chat_id'],
            user_query,
            response
        )
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)