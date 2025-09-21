from model import GeminiModel
from history_manager import HistoryManager
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class GeminiChat:
    
    def __init__(self):
        self.gemini = GeminiModel()
        self.current_model = None
        self.conversation_history = []
        self.session_start = datetime.now()
        self.current_conversation_id = None
        self.current_conversation_name = None
        
        self.history_manager = HistoryManager()
        self.current_conversation_id = self.history_manager.generate_conversation_id()
    
    def load_conversation(self, conversation_id: str = None):
        if not conversation_id:
            return self.select_conversation_menu()
        
        conversation = self.history_manager.load_conversation_by_id(conversation_id)
        if conversation:
            self.current_conversation_id = conversation.get("id")
            self.current_conversation_name = conversation.get("name")
            self.conversation_history = conversation.get("messages", [])
            print(f"Loaded conversation: {self.current_conversation_id[:20]}")
            if self.current_conversation_name:
                print(f"Name: {self.current_conversation_name}")
            print(f"{len(self.conversation_history)} messages loaded")
            return True
        else:
            print(f"Conversation with ID {conversation_id} not found.")
            return False
    
    def select_conversation_menu(self) -> bool:
        recent_conversations = self.history_manager.get_recent_conversations(days=7, limit=100)
        
        if not recent_conversations:
            print("No recent conversations found.")
            return False
        
        print("\n" + "="*60)
        print(" SELECT CONVERSATION TO LOAD")
        print("="*60)
        
        display_conversations = recent_conversations[-10:]
        for i, conv in enumerate(display_conversations, 1):
            summary = self.history_manager.format_conversation_summary(
                conv, self.current_conversation_id
            )
            print(f"\n[{i}] {summary}")
        
        print("\n" + "="*60)
        print("\nEnter conversation number (or 'c' to cancel):")
        
        choice = input(">>> ").strip().lower()
        
        if choice == 'c':
            print("Cancelled.")
            return False
        
        try:
            conv_index = int(choice) - 1
            if 0 <= conv_index < len(display_conversations):
                selected_conv = display_conversations[conv_index]
                
                if len(self.conversation_history) > 0:
                    print("Save current conversation before switching? (y/n)")
                    if input(">>> ").strip().lower() == 'y':
                        self.save_history()
                
                self.current_conversation_id = selected_conv.get("id")
                self.current_conversation_name = selected_conv.get("name")
                self.conversation_history = selected_conv.get("messages", [])
                self.session_start = datetime.now()
                
                print(f" Switched to conversation: {self.current_conversation_id[:20]}")
                if self.current_conversation_name:
                    print(f" Name: {self.current_conversation_name}")
                print(f" {len(self.conversation_history)} messages loaded")
                
                self.display_loaded_conversation()
                
                return True
            else:
                print("Invalid selection.")
                return False
                
        except (ValueError, IndexError):
            print("Invalid selection.")
            return False
    
    def save_history(self, auto_save=False, custom_name=None):
        if not auto_save and not custom_name and not self.current_conversation_name:
            print("\n" + "="*50)
            print(" SAVE CONVERSATION")
            print("="*50)
            print("Enter a name for this conversation (or press Enter to skip):")
            name_input = input(">>> ").strip()
            if name_input:
                self.current_conversation_name = name_input
                custom_name = name_input
        
        conversation_name = custom_name or self.current_conversation_name
        
        success = self.history_manager.save_conversation(
            conversation_id=self.current_conversation_id,
            conversation_name=conversation_name,
            messages=self.conversation_history,
            model=self.current_model,
            session_start=self.session_start,
            auto_save=auto_save
        )
        
        if not success and not auto_save:
            print("Failed to save conversation.")
    
    def save_with_name_menu(self):
        if len(self.conversation_history) == 0:
            print("No conversation to save.")
            return
        
        print("\n" + "="*50)
        print(" SAVE CONVERSATION WITH NAME")
        print("="*50)
        
        print(f"Current ID: {self.current_conversation_id[:20]}")
        if self.current_conversation_name:
            print(f"Current name: {self.current_conversation_name}")
        print(f"Messages: {len(self.conversation_history)}")
        print(f"Duration: {datetime.now() - self.session_start}")
        
        print("\n" + "-"*50)
        print("Enter a name for this conversation:")
        print("(Leave empty to keep current name or use auto-generated title)")
        
        name_input = input(">>> ").strip()
        
        if name_input:
            self.current_conversation_name = name_input
            self.save_history(custom_name=name_input)
            print(f"Conversation saved as: '{name_input}'")
        else:
            self.save_history()
            print("Conversation saved")
    
    def auto_save_history(self):
        if len(self.conversation_history) >= 2:
            self.save_history(auto_save=True)
    
    def clear_history(self):
        if len(self.conversation_history) > 0:
            print("Save current conversation before clearing? (y/n)")
            if input(">>> ").strip().lower() == 'y':
                self.save_with_name_menu()
        
        self.conversation_history = []
        self.current_conversation_id = self.history_manager.generate_conversation_id()
        self.current_conversation_name = None
        self.session_start = datetime.now()
        print(f"Started new conversation with ID: {self.current_conversation_id[:20]}")
    
    def display_help(self):
        print("\n" + "="*50)
        print(" AVAILABLE COMMANDS")
        print("="*50)
        print("/help     - Show this help message")
        print("/clear    - Clear and start new conversation")
        print("/current  - Show current conversation history")
        print("/all      - Show full conversation content")
        print("/history  - Load a previous conversation")
        print("/list     - List all saved conversations")
        print("/info     - Show current conversation info")
        print("/model    - Change model")
        print("/save     - Save current conversation")
        print("/rename   - Rename current conversation")
        print("/delete   - Delete saved conversations")
        print("/exit     - Exit the application")
        print("="*50 + "\n")
    
    def rename_conversation(self):
        print("\n" + "="*50)
        print(" RENAME CURRENT CONVERSATION")
        print("="*50)
        print(f"Current ID: {self.current_conversation_id[:20]}")
        if self.current_conversation_name:
            print(f"Current name: {self.current_conversation_name}")
        else:
            print("Current name: (No custom name)")
        
        print("\nEnter new name (or press Enter to cancel):")
        new_name = input(">>> ").strip()
        
        if new_name:
            self.current_conversation_name = new_name
            self.save_history()
            print(f"Conversation renamed to: '{new_name}'")
        else:
            print("Rename cancelled.")
    
    def display_current_history(self):
        if not self.conversation_history:
            print("No messages in current conversation.")
            return
        
        self.history_manager.display_loaded_conversation(
            messages=self.conversation_history,
            conversation_name=self.current_conversation_name,
            conversation_id=self.current_conversation_id
        )
    
    def display_loaded_conversation(self):
        self.history_manager.display_loaded_conversation(
            messages=self.conversation_history,
            conversation_name=self.current_conversation_name,
            conversation_id=self.current_conversation_id
        )
    
    def display_full_conversation(self):
        self.history_manager.display_full_conversation(
            messages=self.conversation_history,
            conversation_name=self.current_conversation_name,
            conversation_id=self.current_conversation_id
        )
    
    def display_info(self):
        print("\n" + "="*50)
        print(" CURRENT CONVERSATION INFO")
        print("="*50)
        print(f"ID: {self.current_conversation_id}")
        if self.current_conversation_name:
            print(f"Name: {self.current_conversation_name}")
        else:
            print("Name: (No custom name)")
        print(f"Model: {self.current_model}")
        print(f"Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {datetime.now() - self.session_start}")
        print(f"Messages: {len(self.conversation_history)}")
        print("="*50 + "\n")
    
    def list_conversations(self):
        all_conversations = self.history_manager.get_all_conversations(limit=200)
        
        if not all_conversations:
            print("No saved conversations found.")
            return
        
        print("\n" + "="*60)
        print(" SAVED CONVERSATIONS")
        print("="*60)
        
        display_conversations = all_conversations[-20:]
        for i, conv in enumerate(display_conversations, 1):
            summary = self.history_manager.format_conversation_summary(
                conv, self.current_conversation_id
            )
            print(f"\n[{i}] {summary}")
        
        print("\n" + "="*60 + "\n")
    
    def delete_conversations_menu(self):
        all_conversations = self.history_manager.get_all_conversations(limit=20)
        
        if not all_conversations:
            print("No saved conversations to delete.")
            return
        
        print("\n" + "="*60)
        print(" DELETE CONVERSATIONS")
        print("="*60)
        
        for i, conv in enumerate(all_conversations, 1):
            summary = self.history_manager.format_conversation_summary(
                conv, self.current_conversation_id
            )
            print(f"\n[{i}] {summary}")
        
        print("\n" + "="*60)
        print("\nOptions:")
        print("  - Enter conversation number(s) to delete (e.g., '1,3,5')")
        print("  - Enter 'all' to delete all conversations")
        print("  - Enter 'c' to cancel")
        
        choice = input("\n>>> ").strip().lower()
        
        if choice == 'c':
            print("Cancelled.")
            return
        
        if choice == 'all':
            print("\n  Are you sure you want to delete ALL conversations?")
            print("Type 'yes' to confirm:")
            if input(">>> ").strip().lower() == 'yes':
                success = self.history_manager.delete_all_conversations()
                if success:
                    print(" Deleted all conversations")
                    self.conversation_history = []
                    self.current_conversation_id = self.history_manager.generate_conversation_id()
                    self.current_conversation_name = None
                else:
                    print(" Failed to delete conversations")
            return
        
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            conversation_ids_to_delete = []
            
            for idx in indices:
                if 0 <= idx < len(all_conversations):
                    conv = all_conversations[idx]
                    conversation_ids_to_delete.append(conv.get("id"))
            
            if conversation_ids_to_delete:
                print(f"\n Delete {len(conversation_ids_to_delete)} conversation(s)?")
                print("Type 'yes' to confirm:")
                
                if input(">>> ").strip().lower() == 'yes':
                    success = self.history_manager.delete_conversations(conversation_ids_to_delete)
                    if success:
                        print(f" Deleted {len(conversation_ids_to_delete)} conversation(s)")
                        
                        if self.current_conversation_id in conversation_ids_to_delete:
                            self.conversation_history = []
                            self.current_conversation_id = self.history_manager.generate_conversation_id()
                            self.current_conversation_name = None
                            print(f" Started new conversation: {self.current_conversation_id[:20]}")
                    else:
                        print(" Failed to delete conversations")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid selection(s).")
                
        except ValueError:
            print("Invalid input format.")
    
    def run(self):
        print("\n" + "="*60)
        print(" GEMINI AI CHAT APPLICATION")
        print("="*60)
        print(f" Starting new conversation: {self.current_conversation_id[:20]}")
        print(" Use '/history' to load a previous conversation")
        print(" Type '/help' for all available commands\n")
        print("="*60 + "\n")
        self.current_model = self.gemini.select_model(interactive=True)
        print(f"\n Using model: {self.current_model}")
        print("\nStart chatting! (Type '/exit' to quit)\n")
        
        try:
            while True:
                user_input = input("\nYour questions: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.startswith('/'):
                    command = user_input.lower()
                    
                    if command == '/exit':
                        print("\nDo you want to save the conversation before exiting? (y/n)")
                        if input(">>> ").strip().lower() == 'y':
                            self.save_with_name_menu()
                        print("\nGoodbye!")
                        break
                    
                    elif command == '/help':
                        self.display_help()
                        continue
                    
                    elif command == '/clear':
                        self.clear_history()
                        continue
                    
                    elif command == '/current':
                        self.display_current_history()
                        continue
                    
                    elif command == '/all':
                        self.display_full_conversation()
                        continue
                    
                    elif command == '/history':
                        self.load_conversation()
                        continue
                    
                    elif command == '/info':
                        self.display_info()
                        continue
                    
                    elif command == '/list':
                        self.list_conversations()
                        continue
                    
                    elif command == '/delete':
                        self.delete_conversations_menu()
                        continue
                    
                    elif command == '/model':
                        self.current_model = self.gemini.select_model(interactive=True)
                        print(f" Switched to model: {self.current_model}")
                        continue
                    
                    elif command == '/save':
                        self.save_with_name_menu()
                        continue
                    
                    elif command == '/rename':
                        self.rename_conversation()
                        continue
                    
                    else:
                        print(f"Unknown command: {user_input}")
                        print("Type '/help' for available commands")
                        continue
                
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input
                })
                
                print("\nResponse: ", end="", flush=True)
                
                try:
                    response_text = ""
                    for chunk in self.gemini.generate_response(
                        prompt=user_input,
                        model=self.current_model,
                        history=self.conversation_history[:-1], 
                        stream=True
                    ):
                        if chunk.text:
                            response_text += chunk.text
                            print(chunk.text, end="", flush=True)
                    
                    print()  
                    
                    self.conversation_history.append({
                        "role": "model",
                        "content": response_text
                    })
                    
                    self.auto_save_history()
                    
                    max_length = self.history_manager.MAX_HISTORY_LENGTH
                    if len(self.conversation_history) > max_length * 2:
                        self.conversation_history = self.conversation_history[-max_length:]
                        print("\n(Note: Trimmed old messages from memory to save resources)")
                    
                except Exception as e:
                    print(f"\n Error generating response: {e}")
                    if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                        self.conversation_history.pop()
        
        except KeyboardInterrupt:
            print("\n\n Interrupted by user")
            print("Do you want to save the conversation? (y/n)")
            try:
                if input(">>> ").strip().lower() == 'y':
                    self.save_with_name_menu()
            except:
                pass
            print("\nGoodbye! ")


def main():
    try:
        chat = GeminiChat()
        chat.run()
    except Exception as e:
        print(f" Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())