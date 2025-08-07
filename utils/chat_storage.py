import json
from datetime import datetime
from pathlib import Path

class ChatStorage:
    def __init__(self):
        self.storage_dir = Path("chat_history")
        self.storage_dir.mkdir(exist_ok=True)
        
    def create_new_chat(self):
        chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        chat_file = self.storage_dir / f"chat_{chat_id}.json"
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return chat_id
    
    def save_message(self, chat_id, user_query, bot_response):
        chat_file = self.storage_dir / f"chat_{chat_id}.json"
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
            
        history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user_query': user_query,
            'bot_response': bot_response
        })
        
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
            
    def get_chat_history(self, chat_id):
        chat_file = self.storage_dir / f"chat_{chat_id}.json"
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def get_all_chats(self):
        chats = []
        for chat_file in self.storage_dir.glob("chat_*.json"):
            chat_id = chat_file.stem.replace('chat_', '')
            with open(chat_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                if history:
                    chats.append({
                        'id': chat_id,
                        'timestamp': history[0]['timestamp'],
                        'preview': history[0]['user_query'][:50] + '...'
                    })
        return sorted(chats, key=lambda x: x['timestamp'], reverse=True)