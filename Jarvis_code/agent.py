import sys
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
from livekit.plugins import google, noise_cancellation, openai

# Import your custom modules
from Jarvis_prompts import load_prompts
from memory_loop import MemoryExtractor
import os
from mem0 import AsyncMemoryClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config_manager import ConfigManager
config = ConfigManager()

load_dotenv()


class Assistant(Agent):
    def __init__(self, chat_ctx, llm_instance, instructions_text) -> None:
        super().__init__(
            instructions=instructions_text,
            chat_ctx=chat_ctx,
            llm=llm_instance
        )


async def entrypoint(ctx: agents.JobContext):
    # RELOAD CONFIGURATION
    config.load_config()
    
    # Load Dynamic Prompts
    instructions_prompt, reply_prompt = await load_prompts()

    # Get user name and mem0 key from config
    user_id = config.get_user_id()
    full_name = config.get_full_name()
    mem0_key = config.get_mem0_key()
    
    logger.info(f"Fetching initial memories for user_id: {user_id} (Spoken Name: {full_name})")
    
    # STARTUP MEMORY: Fetch existing memories before the agent starts
    try:
        if mem0_key:
            mem0_client = AsyncMemoryClient(api_key=mem0_key)
            
            # Get all memories - returns a LIST directly, not a dict!
            all_memories = await mem0_client.get_all(user_id=user_id)
            
            # Format them into a string - iterate directly over the list
            memory_str = "\n".join([m.get('memory', '') or m.get('text', '') for m in all_memories])
            
            if memory_str:
                memory_str = f"\n\nKNOWN USER HISTORY:\n{memory_str}"
            else:
                memory_str = "\n(No previous history found.)"
        else:
            logger.warning("Mem0 key not found. Skipping startup memory fetch.")
            memory_str = "\n(Memory system disabled - Stateless Mode)"
            
    except Exception as e:
        logger.error(f"Error fetching initial memories: {e}")
        logger.exception("Full traceback:")
        memory_str = "\n(Memory system unavailable)"

    # Get LLM Configuration from config
    llm_config = config.get_llm_config()
    provider = llm_config.get("provider", "google")
    model_name = llm_config.get("model", "gemini-2.5-flash-native-audio-preview-09-2025")
    # Default fallback voices per provider
    default_voice = "Puck" if provider == "google" else "alloy"
    voice_name = llm_config.get("voice", default_voice)

    logger.info(f"Using LLM Provider: {provider}, Model: {model_name}, Voice: {voice_name}")

    # Create LLM instance based on provider
    llm_instance = None
    if provider == "google":
        google_api_key = config.get_api_key("google")
        if not google_api_key:
            logger.error("Google API key not found in config!")
            raise ValueError("Google API key is required when using Google provider")
            
        llm_instance = google.beta.realtime.RealtimeModel(
            model=model_name,
            api_key=google_api_key,
            voice=voice_name
        )
    elif provider == "openai":
        openai_api_key = config.get_api_key("openai")
        if not openai_api_key:
            logger.error("OpenAI API key not found in config!")
            raise ValueError("OpenAI API key is required when using OpenAI provider")
            
        llm_instance = openai.realtime.RealtimeModel(
            model=model_name,
            api_key=openai_api_key,
            voice=voice_name
        )
    else:
        # Fallback to Google
        logger.error(f"Unsupported LLM provider: {provider}. Falling back to Google.")
        google_api_key = config.get_api_key("google")
        if not google_api_key:
            raise ValueError("Google API key is required for fallback")
            
        llm_instance = google.beta.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-09-2025",
            api_key=google_api_key,
            voice="Puck"
        )
    
    # Configure the Session
    session = AgentSession(
        preemptive_generation=True
    )

    # Get the current chat history reference
    current_ctx = session.history.items

    # Inject the startup memory into the context
    initial_ctx = ChatContext()
    initial_ctx.add_message(
        role="assistant", 
        content=f'''The user's spoken name is {full_name}. Internal memory ID is {user_id}.{memory_str}'''
    )
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=initial_ctx, llm_instance=llm_instance, instructions_text=instructions_prompt),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )
    
    # Generate Initial Reply
    await session.generate_reply(
        instructions=reply_prompt
    )
    
    # Start the memory extraction loop
    conv_ctx = MemoryExtractor()
    await conv_ctx.run(current_ctx)


if __name__ == "__main__":
    import sys
    import asyncio
    import time
    
    # --- Windows Specific Fix ---
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    # ----------------------------

    # --- Wait for Valid Config Loop ---
    print("Agent starting... checking for configuration...")
    while True:
        config.load_config()
        lk_url = config.get_api_key("livekit_url")
        lk_key = config.get_api_key("livekit_key")
        lk_secret = config.get_api_key("livekit_secret")

        if lk_url and lk_key and lk_secret:
            active_user_id = config.get_user_id()
            active_full_name = config.get_full_name()
            print(f"Configuration found! Connecting to {lk_url}...")
            print(f"ACTIVE USER PROFILE: ID=[{active_user_id}] NAME=[{active_full_name}]")
            
            # Inject LiveKit credentials
            os.environ["LIVEKIT_URL"] = lk_url
            os.environ["LIVEKIT_API_KEY"] = lk_key
            os.environ["LIVEKIT_API_SECRET"] = lk_secret
            
            # Inject LLM API keys
            google_key = config.get_api_key("google")
            openai_key = config.get_api_key("openai")
            
            if google_key:
                os.environ["GOOGLE_API_KEY"] = google_key
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
            
            # Inject Mem0 Key
            mem0_key = config.get_mem0_key()
            if mem0_key:
                os.environ["MEM0_API_KEY"] = mem0_key
            else:
                print("⚠️  WARNING: Mem0 key not found - Memory system will be disabled")
                
            break
        else:
            print("Waiting for Setup to be completed in browser... (checking again in 2s)")
            time.sleep(2)
    # ------------------------------------------

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))