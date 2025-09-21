import json
import os
from datetime import datetime
from pathlib import Path
import uuid
from typing import Dict, List, Optional


class HistoryManager:
    
    def __init__(self, history_file_path: Path = None):
        if history_file_path:
            self.history_file = history_file_path
        else:
            self.history_file = Path(__file__).parent / "history.json"
        
        self.MAX_HISTORY_LENGTH = 200
        self.MAX_CONVERSATIONS = 200
    
    def generate_conversation_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"conv_{timestamp}_{unique_id}"
    
    def format_conversation_summary(self, conversation: Dict, current_id: str = None) -> str:
        conv_id = conversation.get("id", "unknown")
        conv_name = conversation.get("name", "")
        timestamp = conversation.get("timestamp", "")
        model = conversation.get("model", "unknown")
        messages = conversation.get("messages", [])
        
        try:
            time_obj = datetime.fromisoformat(timestamp)
            time_str = time_obj.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = "unknown time"
        
        if conv_name:
            title = conv_name
        else:
            title = "Empty conversation"
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "")[:50]
                    if len(msg.get("content", "")) > 50:
                        content += "..."
                    title = content
                    break
        
        msg_count = len(messages)
        
        summary = f"ID: {conv_id[:20]}\n    {time_str} | Model: {model} | Messages count: {msg_count} messages\n   Title: {title}"
        
        if conv_id == current_id:
            summary += "\n    CURRENT"
            
        return summary
    
    def load_conversations_data(self) -> Dict:
        if not self.history_file.exists():
            return {"conversations": []}
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or "conversations" not in data:
                return {"conversations": []}
                
            return data
            
        except (json.JSONDecodeError, ValueError, Exception):
            print("Warning: History file corrupted, returning empty structure...")
            return {"conversations": []}
    
    def save_conversations_data(self, data: Dict) -> bool:
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except PermissionError:
            print(f"Permission denied: Cannot write to {self.history_file}")
            return False
        except Exception as e:
            print(f"Could not save history: {e}")
            return False
    
    def save_conversation(self, conversation_id: str, conversation_name: str, 
                         messages: List[Dict], model: str, session_start: datetime, 
                         auto_save: bool = False) -> bool:
        if auto_save and len(messages) < 2:
            return True
            
        try:
            data = self.load_conversations_data()
            
            session_data = {
                "id": conversation_id,
                "name": conversation_name,
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "session_duration": str(datetime.now() - session_start),
                "messages": messages[-self.MAX_HISTORY_LENGTH:]
            }
            
            conversation_exists = False
            for i, conv in enumerate(data["conversations"]):
                if conv.get("id") == conversation_id:
                    data["conversations"][i] = session_data
                    conversation_exists = True
                    break
            
            if not conversation_exists:
                data["conversations"].append(session_data)
            
            if len(data["conversations"]) > self.MAX_CONVERSATIONS:
                data["conversations"] = data["conversations"][-self.MAX_CONVERSATIONS:]
            
            success = self.save_conversations_data(data)
            
            if success and not auto_save:
                print(f"History saved with ID: {conversation_id[:20]}")
                if conversation_name:
                    print(f"Name: {conversation_name}")
                print(f"  File: {self.history_file}")
            
            return success
            
        except Exception as e:
            print(f"Could not save conversation: {e}")
            return False
    
    def load_conversation_by_id(self, conversation_id: str) -> Optional[Dict]:
        data = self.load_conversations_data()
        
        if not data.get("conversations"):
            return None
        
        for conv in data["conversations"]:
            if conv.get("id") == conversation_id:
                return conv
        
        return None
    
    def get_recent_conversations(self, days: int = 7, limit: int = 100) -> List[Dict]:
        data = self.load_conversations_data()
        conversations = data.get("conversations", [])
        
        if not conversations:
            return []
        
        recent_conversations = []
        now = datetime.now()
        
        for conv in conversations:
            try:
                conv_time = datetime.fromisoformat(conv["timestamp"])
                time_diff = now - conv_time
                if time_diff.total_seconds() < (days * 24 * 3600):
                    recent_conversations.append(conv)
            except:
                recent_conversations.append(conv)
        
        return recent_conversations[-limit:]
    
    def get_all_conversations(self, limit: int = 200) -> List[Dict]:
        data = self.load_conversations_data()
        conversations = data.get("conversations", [])
        
        return conversations[-limit:]
    
    def delete_conversations(self, conversation_ids: List[str]) -> bool:
        try:
            data = self.load_conversations_data()
            
            if not data.get("conversations"):
                return True
            
            data["conversations"] = [
                conv for conv in data["conversations"] 
                if conv.get("id") not in conversation_ids
            ]
            
            return self.save_conversations_data(data)
            
        except Exception as e:
            print(f"Error deleting conversations: {e}")
            return False
    
    def delete_all_conversations(self) -> bool:
        try:
            data = {"conversations": []}
            return self.save_conversations_data(data)
            
        except Exception as e:
            print(f"Error deleting all conversations: {e}")
            return False
    
    def display_loaded_conversation(self, messages: List[Dict], conversation_name: str = None, 
                                   conversation_id: str = None):
        if not messages:
            print("No messages in loaded conversation.")
            return
        
        print("\n" + "="*60)
        print(" LOADED CONVERSATION CONTENT")
        if conversation_name:
            print(f" NAME: {conversation_name}")
        if conversation_id:
            print(f" ID: {conversation_id}")
        print(f" MESSAGES: {len(messages)}")
        print("="*60)
        
        for i, msg in enumerate(messages, 1):
            role = "You" if msg["role"] == "user" else "AI"
            print(f"\n[{i}] {role}:")
            content = msg["content"]
            if len(content) > 800:
                print(content[:800] + f"... (truncated, {len(content)} total chars)")
            else:
                print(content)
        
        print("="*60 + "\n")
        print("   Type '/all' to see full content without truncation.\n")
    
    def display_full_conversation(self, messages: List[Dict], conversation_name: str = None, 
                                 conversation_id: str = None):
        if not messages:
            print("No messages in current conversation.")
            return
        
        print("\n" + "="*60)
        print(" FULL CONVERSATION CONTENT")
        if conversation_name:
            print(f" NAME: {conversation_name}")
        if conversation_id:
            print(f" ID: {conversation_id}")
        print(f" MESSAGES: {len(messages)}")
        print("="*60)
        
        for i, msg in enumerate(messages, 1):
            role = "You" if msg["role"] == "user" else "AI"
            print(f"\n[{i}] {role}:")
            print(msg["content"])
        
        print("="*60 + "\n")
