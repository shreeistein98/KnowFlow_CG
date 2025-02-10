# KnowFlow - AI Assistant Platform

A modern, feature-rich AI assistant platform built with FastAPI, Gemini, and Tavily, offering multiple interaction modes and advanced capabilities.

## Key Features

### 1. Smart Web Search & Information Retrieval
- Powered by Tavily Search API - optimized for AI agents
- Advanced content extraction from multiple sources
- Real-time information gathering
- Automatic summarization and content processing
- Clean, relevant results without ads or clutter

### 2. Text Chat
- Real-time conversation with Google's Gemini AI
- Context-aware responses
- Streaming text output
- Markdown support with syntax highlighting

### 3. Local AI Model Support
- Integration with Ollama for local model inference
- Google's Gemma 2B model for offline processing
- Lightweight yet powerful responses
- Privacy-focused local computation
- Markdown formatting and code highlighting

### 4. Image Generation
- Generate images from text descriptions
- High-quality image output (1024x1024)
- Powered by FLUX.1-schnell model
- Download generated images

### 5. RAG (Retrieval-Augmented Generation)
- Upload and process documents for context-aware responses
- Supports multiple file formats (PDF, DOCX, TXT, etc.)
- Semantic search using ChromaDB
- Context-aware responses based on uploaded documents

### 6. Live Drawing Assistant
- Interactive drawing canvas
- Real-time AI assistance
- Color picker and drawing tools
- Screen capture integration
- Voice interaction with audio feedback

### 7. Visual Question Answering
- Ask questions about images using voice
- Multilingual support (including Hindi and Spanish)
- Real-time camera integration
- Voice responses using Google Text-to-Speech

## Technical Stack

### Core Technologies
- **Backend**: FastAPI, Python 3.11
- **AI Models**: 
  - Google Gemini 2.0 Flash for text generation
  - FLUX.1-schnell for image generation
  - Tavily API for web search and content extraction
  - Google's Gemma 2B via Ollama for local processing
- **Database**: ChromaDB for vector storage
- **Frontend**: JavaScript, TailwindCSS

### Key Integrations
- **Tavily Search API**: Advanced web search and content extraction
- **Google Gemini API**: State-of-the-art language model
- **Google Cloud TTS**: Text-to-speech capabilities
- **HuggingFace**: Embedding models and transformers
- **Ollama**: Local model inference

## Setup

### Prerequisites
- Python 3.11
- Git
- For Windows: PowerShell with administrator privileges
- For macOS/Linux: Terminal with sudo access

### Environment Variables
Create a `.env` file with:
```env
GEMINI_API_KEY=your_gemini_api_key
# Get from Google AI Studio: https://makersuite.google.com/app/apikey

TAVILY_API_KEY=your_tavily_api_key
# Get from Tavily AI Dashboard: https://tavily.com/dashboard

HUGGINGFACE_API_KEY=your_huggingface_api_key
# Get from HuggingFace Settings: https://huggingface.co/settings/tokens

LLAMA_CLOUD_API_KEY=your_llama_api_key
# Get from LlamaCloud Dashboard: https://cloud.llama-api.com/

GOOGLE_APPLICATION_CREDENTIALS=credentials/google-cloud-credentials.json (dont change this path)
# Get from Google Cloud Console: https://console.cloud.google.com/apis/credentials
# Download JSON and save in credentials/ folder which is already there, just paste it.
```

The setup scripts will automatically create the credentials directory if it doesn't exist.

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd knowflow
```

2. Choose the appropriate setup method for your operating system:

#### For Windows:
```powershell
# Run PowerShell as Administrator
.\setup.ps1
```

#### For macOS/Linux:
```bash
# Make the setup script executable
chmod +x setup.sh
# Run the setup script
./setup.sh
```

The setup scripts will automatically:
- Install Python 3.11 if not present
- Create a Python virtual environment
- Install required packages
- Install and configure Ollama
- Pull the lama3.2 3B model
- Set up all necessary dependencies

### Running the Application

Start the application:

**Important**: You need to activate the virtual environment in EACH NEW terminal session before running the application.

#### For Windows:
```powershell
# Activate virtual environment (required for each new terminal session)
.\venv\Scripts\Activate.ps1
# Start the FastAPI server
uvicorn main:app --reload
```

#### For macOS/Linux:
```bash
# Activate virtual environment (required for each new terminal session)
source venv/bin/activate
# Start the FastAPI server
uvicorn main:app --reload
```

Access the web interface at:
```
http://localhost:8000
```

To stop the server:

#### For Windows:
1. Press `Ctrl+C` in the PowerShell window (recommended)
2. If the server doesn't stop:
   ```powershell
   # Kill the process
   taskkill /F /IM python.exe
   ```

Note: The kill command forcefully terminates processes. Only use it if `Ctrl+C` doesn't work.

#### For macOS/Linux:
1. Press `Ctrl+C` in the terminal (recommended)
2. If the server doesn't stop:
   ```bash
   # First suspend the process
   Ctrl+Z
   
   # Then find and kill the process on port 8000
   lsof -ti :8000 | xargs kill -9
   ```

Note: The kill commands forcefully terminate processes. Only use them if `Ctrl+C` doesn't work.

## Usage

### Text Chat with Web Search
1. Type your question in the chat input
2. The system will:
   - Search the web using Tavily API
   - Extract relevant content from top sources
   - Generate a comprehensive answer using Gemini
   - Stream the response in real-time

### Local Model Chat
1. Click the microchip icon to enable local model mode
2. Type your question
3. Get responses from the Gemma 2B model running locally
4. Enjoy privacy-focused, offline processing

### Image Generation
1. Click the gallery icon
2. Enter your image description
3. Wait for the image to be generated
4. Download using the download button

### RAG Mode
1. Toggle RAG mode
2. Upload documents
3. Ask questions about the documents

### Live Drawing
1. Click the pencil icon
2. Use drawing tools
3. Speak to get AI assistance

### Visual Q&A
1. Click the video icon
2. Allow camera and microphone access
3. Ask questions about what you see
4. Get voice responses

