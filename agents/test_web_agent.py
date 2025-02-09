import asyncio
from web_agent import WebAgent
import os
from dotenv import load_dotenv

async def test_web_search():
    """
    Test the WebAgent with a specific query about USA election 2024
    """
    try:
        # Initialize WebAgent
        agent = WebAgent()
        
        # Test query
        query = "who won the usa election in 2024"
        print(f"\nSearching for: {query}")
        print("\nFetching results...")
        
        # Process the query and collect responses
        response_text = ""
        async for chunk in agent.process_web_query(query):
            print(chunk, end="", flush=True)  # Print chunks as they come
            response_text += chunk
            
        print("\n\nSearch and response complete!")
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the test
    print("Starting WebAgent test...")
    asyncio.run(test_web_search()) 