import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from db
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
import httpx
import requests
from markdownify import markdownify as md
from dotenv import load_dotenv
import fal_client
from db.db import store_media, create_article, get_article_by_id

load_dotenv()

def url_to_markdown(url: str) -> str:
    """Convert a URL to markdown content by fetching and processing the HTML"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.1 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return md(response.text)
    except Exception as e:
        print(f"Error fetching or processing URL {url}: {str(e)}")
        return f"Failed to fetch content from {url}: {str(e)}"

async def generate_prompt(article_content=None, article_url=None):
    """Generate a prompt using the Qwen model based on an article content or URL"""
    # Create a custom http client without proxies to avoid compatibility issues
    http_client = httpx.Client(base_url="https://integrate.api.nvidia.com/v1")
    
    # Initialize the OpenAI client with the custom http client
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = os.getenv("NVIDIA_API_KEY"),
        http_client = http_client
    )

    # Create user content with article information
    user_content = "Create a detailed text-to-image prompt for a social media meme"
    
    if article_url:
        # Fetch the actual content of the article and convert to markdown
        markdown_content = url_to_markdown(article_url)
        
        # Use a snippet of the markdown content (first 3000 chars to avoid token limits)
        content_snippet = markdown_content[:3000] + "..." if len(markdown_content) > 3000 else markdown_content
        
        user_content += f" based on this article content from {article_url}:\n\n{content_snippet}"
    elif article_content:
        user_content += f" based on this article content: '{article_content[:2000]}...'."  # Limit to 2000 chars for prompt
    else:
        user_content += " based on AI reward hacking concept."
        
    user_content += (" Follow the FLUX framework structure and enhancement layers, with careful attention "
                    "to word order (most important elements first). Include text overlay that's witty and educational.")

    completion = client.chat.completions.create(
        model="qwen/qwen3-next-80b-a3b-thinking",
        messages=[
            {"role":"system","content":"You are an expert in creating detailed, creative prompts for text-to-image models that will generate engaging social media memes following the FLUX Prompt Framework: Subject + Action + Style + Context. Your prompts should use structured descriptions with enhancement layers: Visual Layer (lighting, color palette, composition), Technical Layer (camera settings, lens specs), and Atmospheric Layer (mood, emotional tone). Follow optimal prompt length (30-80 words) and prioritize elements by importance (front-load critical elements). Include specific text integration instructions when needed, placing text in quotation marks with clear placement and style descriptions."},
            {"role":"user","content": user_content}
        ],
        temperature=0.6,
        top_p=0.7,
        max_tokens=4096,
        stream=True
    )

    full_content = ""
    reasoning_done = False
    for chunk in completion:
        reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
        if reasoning:
            print(reasoning, end="")
            reasoning_done = True
        elif reasoning_done and chunk.choices[0].delta.content is not None:
            print("\n--- END OF REASONING ---\n", end="")
            reasoning_done = False
        
        content = chunk.choices[0].delta.content
        if content is not None:
            print(content, end="")
            full_content += content
    
    return full_content

async def generate_image(prompt):
    """Generate an image using fal-ai API"""
    if not prompt:
        print("\nError: Empty prompt")
        return None

    print(f"\n\nGenerating image with prompt: {prompt}\n")
    
    handler = await fal_client.submit_async(
        "fal-ai/alpha-image-232/text-to-image",
        arguments={
            "prompt": prompt
        },
    )
    
    async for event in handler.iter_events(with_logs=True):
        print(event)
    
    result = await handler.get()
    return result

async def process_article_and_generate_media(article_id=None, article_url=None, article_text=None, style="meme"):
    """Process an article and generate media content, storing results in the database"""
    
    # If article_id provided, fetch the article
    if article_id:
        article = await get_article_by_id(article_id)
        if not article:
            print(f"Article with ID {article_id} not found")
            return None
        article_text = article["text"]
    
    # If we have URL but no text, create a new article with actual content
    elif article_url and not article_text:
        try:
            # Fetch article content from URL and store it
            article_markdown = url_to_markdown(article_url)
            # Store only first 10000 chars if it's too long
            stored_text = article_markdown[:10000] + "..." if len(article_markdown) > 10000 else article_markdown
            
            # Create article with actual content
            article_row = await create_article(source=article_url, text=stored_text, user_id=None)
            article_id = article_row["id"]
            article_text = stored_text  # Use this for prompt generation
        except Exception as e:
            print(f"Failed to fetch content from URL, creating empty article: {str(e)}")
            # Fallback to empty article
            article_row = await create_article(source=article_url, text=f"URL-based article (content fetch failed: {str(e)})", user_id=None)
            article_id = article_row["id"]
    
    # If we have text but no article_id, create a new article
    elif article_text and not article_id:
        article_row = await create_article(source="direct input", text=article_text, user_id=None)
        article_id = article_row["id"]
    
    # Generate the prompt using Qwen model
    prompt = await generate_prompt(article_content=article_text, article_url=article_url)
    
    # Generate the image using fal-ai
    image_result = await generate_image(prompt)
    
    if not image_result or "images" not in image_result:
        print("Failed to generate image")
        return None
    
    # Extract the image URL from the nested structure
    # The image result contains a list of image objects with url and metadata
    image_obj = image_result["images"][0]
    media_url = image_obj["url"]  # Extract just the URL string
    
    print(f"\nExtracted image URL: {media_url}")
    
    # Store the media in the database
    media_row = await store_media(
        article_id=article_id,
        prompt=prompt,
        style=style,
        media_type="image",
        media_url=media_url
    )
    
    print(f"\n=== Media stored in database with ID {media_row['id']} ===")
    
    # Return complete result with image metadata
    return {
        "article_id": article_id,
        "media_id": media_row["id"],
        "prompt": prompt,
        "media_url": media_url,
        "image_metadata": image_result["images"][0]  # Include full image metadata for reference
    }

async def main():
    # Example usage
    article_url = "https://www.lesswrong.com/posts/fJtELFKddJPfAxwKS/natural-emergent-misalignment-from-reward-hacking-in"
    result = await process_article_and_generate_media(article_url=article_url)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
