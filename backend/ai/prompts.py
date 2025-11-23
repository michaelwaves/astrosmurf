from tqdm.asyncio import tqdm_asyncio
import asyncio
import httpx
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

async def generate_prompt_with_progress(concept, style, pbar,max_concept_length=500):
    prompt = await create_generation_prompt(concept=concept, max_length=max_concept_length, style=style)
    pbar.update(1)
    return prompt

async def generate_multiple_prompts(concepts,style):
    prompts=[]
    total = len(concepts)
    with tqdm_asyncio(total=total, desc="Generating prompts...") as pbar:
        tasks = [
            generate_prompt_with_progress(concept, style, pbar)
            for concept in concepts
        ]

        prompts = await asyncio.gather(*tasks)
    return prompts


async def create_generation_prompt(concept, max_length, style="meme"):
    # Create generation prompt
    prompt = f"""Create a detailed text-to-image prompt for a social media {style}
    
    based on this concept: '{concept[:max_length]}...'.Follow the FLUX framework structure and enhancement layers, with careful attention "
                    "to word order (most important elements first)")
    """
    system_prompt=f"""You are an expert in creating detailed, creative prompts for text-to-image models that will generate engaging social media {style} following the FLUX Prompt Framework: Subject + Action + Style + Context. Your prompts should use structured descriptions with enhancement layers: Visual Layer (lighting, color palette, composition), Technical Layer (camera settings, lens specs), and Atmospheric Layer (mood, emotional tone). Follow optimal prompt length (30-80 words) and prioritize elements by importance (front-load critical elements). Include specific text integration instructions when needed, placing text in quotation marks with clear placement and style descriptions."""
    prompt = await generate_prompt_fast(prompt, system_prompt=system_prompt)
    return prompt

async def generate_prompt(prompt:str="", system_prompt:str=""):
    """Generate a prompt using the Qwen model based on an article content or URL"""
    # Create a custom http client without proxies to avoid compatibility issues
    http_client = httpx.Client(base_url="https://integrate.api.nvidia.com/v1")
    
    # Initialize the OpenAI client with the custom http client
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = os.getenv("NVIDIA_API_KEY"),
        http_client = http_client
    )

    completion = client.chat.completions.create(
        model="qwen/qwen3-next-80b-a3b-thinking",
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content": prompt}
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



async def generate_prompt_fast(prompt:str="", system_prompt:str=""):
    # Create a custom http client without proxies to avoid compatibility issues
    http_client = httpx.Client(base_url="https://integrate.api.nvidia.com/v1")
    
    # Initialize the OpenAI client with the custom http client
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = os.getenv("NVIDIA_API_KEY"),
        http_client = http_client
    )

    completion = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-nano-8b-v1",
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content": prompt}
        ],
        temperature=0.6,
        top_p=0.7,
        max_tokens=2048,
        stream=False
    )

    text = completion.choices[0].message.content
    print(text)
    return text


if __name__ == "__main__":
    asyncio.run(generate_prompt_fast("make a prompt for image of person singing in the rain. Return ONLY the prompt","you are an image_gen model"))
