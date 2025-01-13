import logging
from urllib.parse import urlparse, quote_plus
from datetime import datetime
from playwright.async_api import async_playwright
import asyncio
import os
import aiohttp
from typing import List
import time
import random

class CrawlerAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Get credentials from environment variables
        self.search_api_key = os.getenv("SEARCH_API_KEY")
        self.search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        
        if not self.search_api_key or not self.search_engine_id:
            raise ValueError("SEARCH_API_KEY and SEARCH_ENGINE_ID must be set in environment variables")
        
        # Base URL for Google Custom Search API
        self.base_url = "https://customsearch.googleapis.com/customsearch/v1"
        
        # Different user agents to rotate through
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36'
        ]
    
    async def search_urls(self, query: str, num_results: int = 3) -> List[str]:
        """Search using Google Custom Search API and return URLs"""
        try:
            # Ensure num_results doesn't exceed API limit
            num_results = min(num_results, 3)
            
            # Construct search URL with only essential parameters
            encoded_query = quote_plus(query)
            search_url = (
                f"{self.base_url}?"
                f"key={self.search_api_key}&"
                f"cx={self.search_engine_id}&"
                f"q={encoded_query}&"
                f"num={num_results}"  # Get 3 results
            )
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'items' in data:
                            # Log URLs from search
                            self.logger.info("=== Search API Results ===")
                            urls = []
                            for item in data['items']:
                                self.logger.info(f"URL: {item['link']}")
                                urls.append(item['link'])
                            self.logger.info("=== End of Search Results ===")
                            return urls[:num_results]
                    else:
                        error_data = await response.json()
                        error_msg = f"Search API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                        self.logger.error(error_msg)
            
            return []
                        
        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}")
            return []
            
    async def render_with_playwright(self, url: str, request_index: int) -> str:
        """Use Playwright to render the page and get content"""
        async with async_playwright() as p:
            # Use different user agent for each request
            user_agent = self.user_agents[request_index % len(self.user_agents)]
            
            # Launch browser with improved configurations
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--no-first-run',
                    '--no-zygote',
                    '--deterministic-fetch',
                    '--disable-features=IsolateOrigins',
                    '--disable-site-isolation-trials',
                    '--window-size=1920,1080',
                    '--disable-blink-features=AutomationControlled',
                    f'--user-agent={user_agent}'  # Set user agent at browser level
                ]
            )
            
            # Create a browser context with request-specific settings
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=user_agent,
                bypass_csp=True,
                ignore_https_errors=True,
                java_script_enabled=True,
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'DNT': '1',
                    'X-Request-ID': f'req-{request_index}-{int(time.time())}'  # Add unique request ID
                }
            )
            
            # Create new page in context
            page = await context.new_page()
            
            try:
                # Configure shorter timeouts
                page.set_default_timeout(15000)  # 15 seconds timeout
                page.set_default_navigation_timeout(15000)
                
                # Add JavaScript to mask automation
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    window.chrome = {
                        runtime: {}
                    };
                """)
                
                # Go to URL with optimized waiting strategy
                try:
                    await page.goto(
                        url, 
                        wait_until="domcontentloaded",  # Changed to faster domcontentloaded
                        timeout=15000
                    )
                    # Shorter random delay
                    await page.wait_for_timeout(1000)
                except Exception as e:
                    self.logger.warning(f"Navigation failed for {url}: {str(e)}")
                    return "Navigation failed: Could not load page content"
                
                # Quick scroll for lazy content
                await page.evaluate("""
                    window.scrollTo(0, document.body.scrollHeight);
                    new Promise((resolve) => {
                        setTimeout(resolve, 500);
                    });
                """)
                
                # Get content with improved extraction
                content = await page.evaluate('''() => {
                    // Function to clean text
                    const cleanText = (text) => {
                        return text
                            .replace(/\\s+/g, ' ')
                            .replace(/[\\r\\n]+/g, ' ')
                            .replace(/\\t/g, ' ')
                            .replace(/\\u00a0/g, ' ')
                            .replace(/\\u200b/g, '')
                            .replace(/\\s+/g, ' ')
                            .trim();
                    };
                    
                    // Check for CAPTCHA or bot detection with more specific patterns
                    const captchaIndicators = [
                        'captcha',
                        'robot check',
                        'bot detection',
                        'verify you are human',
                        'security check',
                        'cloudflare',
                        'ddos protection',
                        'please prove you are human'
                    ];
                    
                    const pageText = document.body.innerText.toLowerCase();
                    if (captchaIndicators.some(indicator => pageText.includes(indicator))) {
                        return '[CAPTCHA_DETECTED] This page requires human verification.';
                    }

                    // Remove unwanted elements
                    const elementsToRemove = [
                        'script',
                        'style',
                        'iframe',
                        'header',
                        'footer',
                        'nav',
                        'noscript',
                        '[class*="cookie"]',
                        '[class*="popup"]',
                        '[class*="banner"]',
                        '[class*="newsletter"]',
                        '[class*="subscribe"]',
                        '[class*="advertisement"]',
                        '[class*="social-share"]'
                    ];
                    
                    elementsToRemove.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => el.remove());
                    });
                    
                    // Try to get main content first with expanded selectors
                    const mainSelectors = [
                        'article',
                        'main',
                        '[role="main"]',
                        '.article-content',
                        '.post-content',
                        '.entry-content',
                        '.main-content',
                        '#main-content',
                        '.content',
                        '#content',
                        '.blog-post',
                        '.article-body',
                        '.post-body',
                        '.page-content'
                    ];
                    
                    for (const selector of mainSelectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            const text = cleanText(element.innerText);
                            if (text.length > 100) {  // Ensure we have meaningful content
                                return text;
                            }
                        }
                    }
                    
                    // Get all paragraphs with better filtering
                    const paragraphs = Array.from(document.querySelectorAll('p'))
                        .filter(p => {
                            const text = cleanText(p.innerText);
                            const wordCount = text.split(' ').length;
                            return wordCount > 10 &&  // Filter out short paragraphs
                                   !text.toLowerCase().includes('cookie') &&
                                   !text.toLowerCase().includes('subscribe') &&
                                   !text.toLowerCase().includes('newsletter');
                        })
                        .map(p => cleanText(p.innerText))
                        .filter(text => text.length > 50);  // Additional length filter
                    
                    if (paragraphs.length > 0) {
                        return paragraphs.join('\\n\\n');  // Add proper paragraph separation
                    }
                    
                    // Last resort: Get all visible text
                    const bodyText = cleanText(document.body.innerText);
                    return bodyText.length > 100 ? bodyText : "No meaningful content found";
                }''')
                
                return content.strip() if content else ""
                
            except Exception as e:
                self.logger.error(f"Playwright error for {url}: {str(e)}")
                return ""
            finally:
                await context.close()
                await browser.close()

    async def process_query(self, query: str) -> str:
        """Main method to search and crawl content"""
        try:
            # First get URLs from search
            self.logger.info(f"Starting search for query: {query}")
            urls = await self.search_urls(query)
            if not urls:
                return "No URLs found for the query."

            # Process URLs fully in parallel (no semaphore needed anymore)
            async def process_url(url, index):
                try:
                    self.logger.info(f"Processing URL {index}/{len(urls)}: {url}")
                    async with asyncio.timeout(20):
                        # Add small random delay for each request to make them look more natural
                        await asyncio.sleep(random.uniform(0.1, 0.5))
                        content = await self.render_with_playwright(url, index)
                        if content:
                            if content.startswith('[CAPTCHA_DETECTED]'):
                                self.logger.warning(f"CAPTCHA detected on {url}")
                            elif content.startswith('Navigation failed:'):
                                self.logger.warning(f"Navigation failed on {url}")
                            else:
                                self.logger.info(f"Successfully extracted content from {url}")
                                return content
                except asyncio.TimeoutError:
                    self.logger.error(f"Timeout processing {url}")
                except Exception as e:
                    self.logger.error(f"Error processing URL {url}: {str(e)}")
                return None

            # Process all URLs truly concurrently
            tasks = [process_url(url, i) for i, url in enumerate(urls)]
            results = await asyncio.gather(*tasks)
            contents = [r for r in results if r]
            
            if not contents:
                return "No content could be extracted from URLs."
            
            self.logger.info(f"Successfully processed {len(contents)} out of {len(urls)} URLs")
            
            # Join contents with clear separation
            return "\n\n=== Source {0}/{1} ===\n\n".join(
                [f"{i+1}/{len(urls)}: {content}" for i, content in enumerate(contents)]
            )
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
