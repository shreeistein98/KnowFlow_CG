import google.generativeai as genai
from typing import AsyncGenerator
import os
from .crawler_agent import CrawlerAgent

class WebAgent:
    def __init__(self):
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.crawler = CrawlerAgent()
        
    async def process_web_query(self, query: str):
        try:
            # Get content using the combined crawler functionality
            scraped_content = await self.crawler.process_query(query)
            
            # Create a more focused prompt for Gemini
            prompt = f""" 
            Please find relevant inforamtion about this:{query} from the following content:{scraped_content}
            NOTE: If there is no direct answer then analyze the given content to reply with the most relevant information.
            Once you get the answer act as if you already knew this information,dont mention about the given content."""

            # Send to Gemini
            response = await self.model.generate_content_async(prompt, stream=True)
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error processing web query: {str(e)}"

