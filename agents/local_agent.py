import aiohttp
from typing import AsyncGenerator
import json

class LocalAgent:
    def __init__(self):
        # Ollama API endpoint (default local installation)
        self.api_url = "http://localhost:11434/api/generate"
        # Using Llama 3.2 3B - Meta's latest multilingual model optimized for:
        # - Following instructions
        # - Summarization
        # - Prompt rewriting
        # - Tool use
        # Supports: English, German, French, Italian, Portuguese, Hindi, Spanish, and Thai
        self.model = "llama3.2"
        
        # System prompt to improve formatting
        self.system_prompt = """You are a helpful AI assistant. Please format your responses clearly:
- Use proper markdown formatting
- Wrap code blocks with ```language_name
- Use bullet points and numbered lists appropriately
- Separate paragraphs with blank lines
- Use bold and italics for emphasis
"""
        
    async def get_streaming_response(self, message: str) -> AsyncGenerator[str, None]:
        """
        Get streaming response from Ollama API using Llama 3.2 model.
        
        Args:
            message (str): User's input message
            
        Yields:
            str: Response chunks from the model
        """
        try:
            # Prepare the request payload with system prompt
            payload = {
                "model": self.model,
                "prompt": f"{self.system_prompt}\n\nUser: {message}\n\nAssistant:",
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            current_response = ""
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload) as response:
                    # Read and process the streaming response
                    async for line in response.content:
                        if line:
                            try:
                                # Decode and parse the JSON response
                                chunk = json.loads(line.decode('utf-8'))
                                # Accumulate response and format
                                if chunk.get("response"):
                                    current_response += chunk["response"]
                                    # Only yield complete sentences or code blocks
                                    if any(char in current_response for char in ".!?\n```"):
                                        yield current_response
                                        current_response = ""
                            except json.JSONDecodeError:
                                continue
                    
                    # Yield any remaining response
                    if current_response:
                        yield current_response
                                
        except Exception as e:
            print(f"Error in LocalAgent streaming: {e}")
            yield f"Error: {str(e)}" 