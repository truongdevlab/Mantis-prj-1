import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
import io

# load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
chat = None

# function to initialize a new chat session
def init_chat():
    global chat
    # use Gemini 2.5 model
    chat = client.chats.create(model="gemini-2.5-flash")
    print("New chat session initialized with Gemini!")

# function to send text messages
def send_text_message():
    # if no chat session exists, initialize a new one
    if chat is None:
        init_chat()

    # get message from user
    message = input("Enter your message: ")
    if not message.strip():
        print("Message cannot be empty!")
        return
    
    # send message and get response
    try:
        response = chat.send_message(message)
        print(f"\nGemini: {response.text}\n")
    except Exception as e:
        print(f"Error: {str(e)}")

# function to send messages with images
def send_image_message():
    if chat is None:
        init_chat()
    
    # input image path
    image_path = input("Enter image path (name.datatype): ")
    if not os.path.exists(image_path):
        print("File does not exist!")
        return
    
    try:
        # open and process image
        img = Image.open(image_path)
        
        # convert image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format)
        img_byte_arr = img_byte_arr.getvalue()
        
        # send image to Gemini
        message = input("Enter message with image (optional): ")
        contents = [
            types.Part.from_bytes(
                data=img_byte_arr,
                mime_type=f'image/{img.format.lower()}'
            )
        ]
        
        if message.strip():
            contents.append(message)
        
        # send message and get response
        response = chat.send_message(contents)
        print(f"\nGemini: {response.text}\n")

    except Exception as e:
        print(f"Error processing image: {str(e)}")

# function to display chat history
def show_chat_history():
    if chat is None:
        print("No chat history yet!")
        return
    
    # get chat history
    history = chat.get_history()

    if not history:
        print("No chat history yet!")
        return
    
    print("\n=== CHAT HISTORY ====")
    for i, message in enumerate(history):
        role = "You" if message.role == "user" else "Gemini"
        print(f"{i+1}. {role}: {message.parts[0].text}")
    print("===================\n")

# function to clear chat history
def clear_chat():
    global chat
    chat = None
    print("Chat history has been cleared!")

# function to display menu
def show_menu():
    print("\n=== GEMINI AI CHAT APPLICATION ===")
    print("1. Send text message")
    print("2. Send message with image")
    print("3. View chat history")
    print("4. Clear chat history")
    print("5. Exit")
    print("=================================")

# main function
def main():
    print("Welcome to Gemini AI Chat Application!")
    print("Connecting to Gemini...")
    
    # check API key
    if not GEMINI_API_KEY:
        print("Error: API key not found. Make sure you have set GEMINI_API_KEY in the .env file")
        return
    
    # initialize chat session
    init_chat()
    
    # create loop to continuously receive commands
    while True:

        # display menu and get choice
        show_menu()
        choice = input("Choose an option (1-5): ")
        
        # option 1 to send text message
        if choice == "1":
            send_text_message()

        # option 2 to send message with image
        elif choice == "2":
            send_image_message()
        
        # option 3 to view chat history
        elif choice == "3":
            show_chat_history()

        # option 4 to clear chat history
        elif choice == "4":
            clear_chat()

        # option 5 to exit application
        elif choice == "5":
            print("Thank you for using the application! Goodbye!")
            break

        else:
            print("Invalid choice! Please try again.")


if __name__ == "__main__":
    main()