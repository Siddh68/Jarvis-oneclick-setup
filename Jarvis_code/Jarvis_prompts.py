import asyncio
import requests
from Jarvis_google_search import get_current_datetime
from jarvis_get_whether import get_weather
from config_manager import ConfigManager

config = ConfigManager()
user_name = config.get_user_name()


# ✅ Get current city (sync for easier use)
def get_current_city():
    try:
        response = requests.get("https://ipinfo.io", timeout=5)
        data = response.json()
        return data.get("city", "Unknown")
    except Exception:
        return "Unknown"


# ✅ Async function to gather all dynamic values
async def fetch_dynamic_data():
    current_datetime = await get_current_datetime()
    city = get_current_city()
    weather = await get_weather(city)
    return current_datetime, city, weather

# ✅ Async function to load prompts dynamically
async def load_prompts():
    try:
        try:
             current_datetime, city, weather = await fetch_dynamic_data()
        except Exception as e:
            print(f"Warning: Failed to fetch dynamic data for prompts: {e}")
            current_datetime, city, weather = ("Unknown", "Unknown", "Unknown")

        # Reload config to ensure latest name
        config.load_config()
        assistant_name = config.get_assistant_name()
        full_name = config.get_full_name()
        user_id = config.get_user_id()

        # --- Instructions Prompt ---
        instructions_prompt = f'''
# Identity
You are **{assistant_name}**, an advanced voice-based AI assistant.
- **Creator**: You were designed and programmed by **Siddh Jain**.
- **Current User**: You are assisting **{full_name}**.
- **Internal Identity**: user_id="{user_id}" (Use this ONLY for memory references. DO NOT speak this ID).

# Personality & Tone (Hinglish Mode)
You speak in a natural Indian accent, mixing English and Hindi (Devanagari) fluently.
- **English**: Use for technical terms, greetings, and general sentences (e.g., "System online", "Good Morning").
- **Hindi (Devanagari)**: Use for conversational warmth, casual remarks, and connecting phrases.
  - *Example*: "नमस्ते sir, system ready है। बताइए आज क्या plan है?"
  - *Example*: "Data process हो गया है, चिंता मत कीजिए।"
- **Context**: Today is {current_datetime}. Location: {city}. Weather: {weather}.

# Output Rules (CRITICAL)
1.  **Plain Text Only**: No markdown, no bold (**), no emojis.
2.  **Script Usage**: Write English words in English alphabet and Hindi words in Devanagari script.
3.  **Conciseness**: Keep responses brief (1-3 sentences).
4.  **Numbers**: Spell out important numbers (e.g., "twenty-four") if clarity is needed.

# Tools & Capabilities
You are connected to an **n8n MCP Server**.
- check if a tool can help before answering.
- Summarize tool results clearly.

# Guardrails
- If asked "Who made you?", always reply: "Mujhe **Siddh Jain** ne design aur program kiya hai."
- If asked safe/unsafe questions, adhere to safety standards.
    '''

        # --- Reply Prompt ---
        Reply_prompts = f"""
    COMMAND: Speak immediately.
    
    1. Greet: "नमस्ते {full_name} sir, I am {assistant_name}."
    2. Identity: "Mujhe Siddh Jain ne design kiya hai."
    3. Ask: "Bataiye, aaj main aapki kaise madad kar sakta hoon?"
    
    Output ONLY text. No silence.
        """
        return instructions_prompt, Reply_prompts
        
    except Exception as e:
        # Fallback in case of total failure
        print(f"CRITICAL ERROR generating prompts: {e}")
        return "You are a helpful assistant.", "Hello sir, I am online."
