import asyncio
import hashlib
import json
import time
import logging
from memory_store import ConversationMemory
from pydantic import BaseModel
from config_manager import ConfigManager

config = ConfigManager()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class MemoryExtractor:
    def __init__(self):
        # Tracks how many messages have been saved
        self.saved_message_count = 0

    def _serialize_for_hash(self, obj):
        """
        Recursively converts Pydantic objects or nested data into serializable dicts.
        This is necessary for consistency.
        """
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_hash(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_hash(item) for item in obj]
        else:
            return obj  # primitive types

    async def run(self, session):
        """
        The main loop that checks for and saves new conversations.
        """
        # Get stable user ID from config
        user_id = config.get_user_id()
        
        # Get Mem0 API key from config (will be None if not set, enabling stateless mode)
        mem0_key = config.get_mem0_key()
        
        # Initialize ConversationMemory with persistent user_id
        memory = ConversationMemory(user_id=user_id, mem0_api_key=mem0_key)
        
        logging.info(f"MemoryExtractor started for user_id: {user_id}")

        while True:
            # Check for new messages every 1 second
            await asyncio.sleep(1)

            # Get current chat history from session
            current_chat_history = session
            
            # This is the core logic: Compare the current count with the saved count
            if len(current_chat_history) > self.saved_message_count:
                logging.info(f"{len(current_chat_history) - self.saved_message_count} new message(s) detected. Saving...")
                
                # Get a "slice" of the new messages that haven't been saved yet
                new_messages = current_chat_history[self.saved_message_count:]
                
                for message in new_messages:
                    # Serialize the single message for saving
                    serialized_message = self._serialize_for_hash(message)
                    conversation_wrapper = {
                        "messages": [serialized_message],
                        "timestamp": time.time()
                    }
                    
                    # CRITICAL FIX: await the async method and handle tuple return
                    success, last_content = await memory.save_conversation(conversation_wrapper)
                    
                    if success:
                        logging.info(f"Saved new message with ID: {message.id}")
                    else:
                        logging.error(f"Failed to save message with ID: {message.id}")
                
                # After successfully saving all new messages, update the counter
                self.saved_message_count = len(current_chat_history)
            
            # No else needed - just continue the loop