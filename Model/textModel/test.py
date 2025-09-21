from model import GeminiModel

def main():
    try:
        gemini = GeminiModel()
        print("Gemini client initialized successfully")
    except Exception as e:
        print(f" Error: {e}")
        return
    
    prompt = input("\nEnter your prompt: ").strip()
    
    if not prompt:
        print("No prompt entered. Exiting...")
        return
    
    print(f"\nTesting with prompt: '{prompt}'")
    print("-" * 50)
    
    results = gemini.test_all_models(prompt)
    
    for model_name, result in results.items():
        print(f"\n{model_name}:")
        if result["status"] == "success":
            print(f" {result['response']}")
        else:
            print(f" Error: {result['error']}")

if __name__ == "__main__":
    main()