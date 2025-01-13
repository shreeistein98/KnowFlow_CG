# KnowFlow

A modern, feature-rich AI assistant platform built with FastAPI, Pydantic, Playwright, offering multiple interaction modes and advanced capabilities like live interaction, Web search on the go, Product Recognition, & much more.

## Features

### 1. Text Chat
- Real-time conversation with Gemini AI
- Context-aware responses
- Streaming text output
- Markdown support with syntax highlighting

### 2. Image Generation
- Generate images from text descriptions
- High-quality image output (1024x1024)
- Powered by FLUX.1-schnell model
- Download generated images

### 3. RAG (Retrieval-Augmented Generation)
- Upload and process documents for context-aware responses
- Supports multiple file formats (PDF, DOCX, TXT, etc.)
- Semantic search using ChromaDB
- Context-aware responses based on uploaded documents

### 4. Web Search
- Real-time web search and content extraction
- Smart content filtering and processing
- Integrated with Google Custom Search API
- Bypass CAPTCHA and bot detection

### 5. Live Drawing Assistant
- Interactive drawing canvas
- Real-time AI assistance
- Color picker and drawing tools
- Screen capture integration
- Voice interaction with audio feedback

### 6. Visual Question Answering
- Ask questions about images using voice
- Multilingual support (including Hindi and Spanish)
- Real-time camera integration
- Voice responses using Google Text-to-Speech

## Setup

### Prerequisites
- Python 3.8+

### Environment Variables
Create a `.env` file with the following:
```env
GEMINI_API_KEY=your_gemini_api_key
SEARCH_API_KEY=your_google_search_api_key
SEARCH_ENGINE_ID=your_search_engine_id
GOOGLE_APPLICATION_CREDENTIALS=path_to_google_credentials.json
LLAMA_CLOUD_API_KEY=your_llama_api_key
```

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd knowflow
```

2. Make the setup script executable:
```bash
chmod +x setup.sh
```

3. Run the setup script:
```bash
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Activate the virtual environment
- Install all required packages from requirements.txt
- Install Playwright browsers
- Set up all necessary dependencies

### Running the Application

After installation, you can start the application using:
```bash
source venv/bin/activate  # If not already in the virtual environment
uvicorn main:app --reload
```

Then open your browser and navigate to:
```
http://localhost:8000
```

To stop the server, you can use:
```bash
lsof -ti :8000 | xargs kill -9
```

## Usage

### Text Chat
- Simply type your message and press enter
- Supports markdown formatting
- Copy button for responses

### Image Generation
- Click the gallery icon
- Enter your image description
- Wait for the image to be generated
- Download using the download button

### RAG Mode
- Toggle RAG mode using the switch
- Upload documents using the file button
- Ask questions about the uploaded documents

### Web Search
- Click the globe icon
- Enter your search query
- Get real-time web search results

### Live Drawing
- Click the pencil icon
- Use drawing tools (pencil, eraser)
- Adjust line width and color
- Clear canvas as needed
- Speak to get AI assistance

### Visual Q&A
- Click the video icon
- Allow camera and microphone access
- Ask questions about what you see
- Get voice responses in multiple languages

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 