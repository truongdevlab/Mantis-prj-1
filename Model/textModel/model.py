import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class GeminiModel:
    
    AVAILABLE_MODELS = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ]
    
    THINKING_SUPPORTED_MODELS = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]
    
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.tools = [types.Tool(googleSearch=types.GoogleSearch())]
    
    def get_available_models(self):
        return self.AVAILABLE_MODELS
    
    def select_model(self, interactive=True):
        if not interactive:
            return self.DEFAULT_MODEL
        
        print("\nAvailable models:")
        for i, m in enumerate(self.AVAILABLE_MODELS, start=1):
            print(f"{i}. {m}")
        print(f"Enter a number to select model, or press Enter to use default ({self.DEFAULT_MODEL}):")
        
        choice = input("Your choice: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(self.AVAILABLE_MODELS):
            return self.AVAILABLE_MODELS[int(choice) - 1]
        else:
            return self.DEFAULT_MODEL
    
    def generate_response(self, prompt, model=None, history=None, stream=True):
        if model is None:
            model = self.DEFAULT_MODEL
        
        contents = []
        
        if history:
            for item in history:
                contents.append(
                    types.Content(
                        role=item["role"],
                        parts=[types.Part.from_text(text=item["content"])]
                    )
                )
        
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        )
        
        config_params = {"tools": self.tools}
        
        if model in self.THINKING_SUPPORTED_MODELS:
            config_params["thinking_config"] = types.ThinkingConfig(thinking_budget=-1)
        
        generate_content_config = types.GenerateContentConfig(**config_params)
        
        if stream:
            return self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            )
        else:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=generate_content_config,
            )
            return response.text
    
    def test_all_models(self, prompt):
        results = {}
        
        for model in self.AVAILABLE_MODELS:
            print(f"\n{'='*50}")
            print(f"Testing model: {model}")
            print(f"{'='*50}")
            
            try:
                response_text = ""
                for chunk in self.generate_response(prompt, model=model, stream=True):
                    if chunk.text:
                        response_text += chunk.text
                        print(chunk.text, end="", flush=True)
                
                results[model] = {
                    "status": "success",
                    "response": response_text
                }
                print("\n")
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(error_msg)
                results[model] = {
                    "status": "error",
                    "error": error_msg 
                }
        
        return results