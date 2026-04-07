import os
import json
import re
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the client
client = Groq()

def remove_base64_images(text: str) -> str:
    """
    Finds and removes massive base64 image strings from the markdown.
    This prevents token limits from exploding due to embedded images.
    """
    # Matches markdown image format containing base64 data
    return re.sub(r'!\[.*?\]\(data:image/.*?;base64,.*?\)', '[IMAGE REMOVED]', text)

def parse_markdown_to_json(markdown_text: str) -> dict:
    """
    Takes a Markdown text, cleans base64 images, chunks it if necessary, 
    uses Groq to parse it, and returns a merged structured dictionary.
    """
    system_prompt = """
    You are an expert in data extraction. Your task is to analyze the following text 
    coming from a PDF formatted in noisy Markdown, clean it, and structure it.
    You must return ONLY a valid JSON object with the following structure:
    {
        "summary": "A brief summary of the text provided",
        "key_concepts": ["concept1", "concept2"],
        "clean_content": "The main text corrected and well-written, removing noise from broken headers or footers"
    }
    """

    # 1. Clean base64 images to drastically reduce token size
    cleaned_text = remove_base64_images(markdown_text)

    # 2. Setup chunking (Groq limit is 12k TPM. ~30,000 characters is ~7,500 tokens)
    chunk_size = 30000 
    chunks = [cleaned_text[i:i+chunk_size] for i in range(0, len(cleaned_text), chunk_size)]
    
    combined_result = {
        "summary": "",
        "key_concepts": [],
        "clean_content": ""
    }

    for index, chunk in enumerate(chunks):
        try:
            print(f"Sending chunk {index + 1} of {len(chunks)} to Groq...")
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}, 
                temperature=0.1, 
            )
            
            # Parse the response for this specific chunk
            chunk_json = json.loads(chat_completion.choices[0].message.content)
            
            # Merge the results into our main dictionary
            combined_result["summary"] += chunk_json.get("summary", "") + " "
            combined_result["key_concepts"].extend(chunk_json.get("key_concepts", []))
            combined_result["clean_content"] += chunk_json.get("clean_content", "") + "\n\n"

            # 3. Respect Rate Limits: Pause before sending the next chunk
            if index < len(chunks) - 1:
                print("Waiting 60 seconds to reset Groq's TPM limit...")
                time.sleep(60) # Wait 1 minute so the 12,000 token limit resets
                
        except Exception as e:
            print(f"Error processing chunk {index + 1} with Groq: {e}")
            # If a chunk fails, we return what we have so far instead of crashing entirely
            return combined_result
            
    # Final cleanup of the merged data
    combined_result["key_concepts"] = list(set(combined_result["key_concepts"])) # Remove duplicates
    combined_result["summary"] = combined_result["summary"].strip()
    combined_result["clean_content"] = combined_result["clean_content"].strip()

    return combined_result