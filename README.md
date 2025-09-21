# Gemini AI Chat Application

A Python-based chat application that interacts with Google's Gemini AI model, supporting both text and image-based conversations.

## Features

- Text-based conversations with Gemini AI
- Image analysis and discussion capabilities
- Chat history management
- Interactive command-line interface
- Support for multiple image formats

## Prerequisites

Before running the application, you need to have:

1. Python installed on your system
2. Required Python packages:
   - `google-ai-generativelanguage` (Google's Generative AI library)
   - `python-dotenv` (for environment variable management)
   - `Pillow` (for image processing)

## Setup

1. Clone this repository
2. Create a `.env` file in the root directory
3. Add your Gemini API key to the `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

Run the application:
```bash
python app.py
```

### Menu Options

1. **Send Text Message**: Send text-only messages to Gemini AI
2. **Send Image Message**: Upload and discuss images with Gemini AI
3. **View Chat History**: Review your conversation history
4. **Clear Chat History**: Start a fresh conversation
5. **Exit**: Close the application

### Image Support

When sending images:
- Ensure the image file is in the correct path
- Supported formats include common image types (PNG, JPG, etc.)
- You can optionally add text context with your image

## Error Handling

The application includes robust error handling for:
- Missing API keys
- Invalid file paths
- Image processing errors
- API communication issues

## Contributing

Feel free to submit issues and enhancement requests.

## License

This project is open-source and available under the MIT License.

## Note

This application uses the Gemini 2.5 Flash model for optimal performance and response quality.