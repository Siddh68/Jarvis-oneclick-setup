import os
from datetime import datetime
from typing import List, Dict, Union, Tuple
import logging
from mem0 import AsyncMemoryClient
from config_manager import ConfigManager

config = ConfigManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationMemory:
    """Handles persistent conversation memory for users using Mem0 cloud storage (Async)"""
    
    def __init__(self, user_id: str, mem0_api_key: str = None):
        self.user_id = user_id
        
        # Initialize Mem0 client - try multiple sources for API key
        api_key = mem0_api_key or config.get_api_key("mem0") or os.getenv("MEM0_API_KEY")
        
        if api_key:
            self.memory_client = AsyncMemoryClient(api_key=api_key)
            logger.info(f"ConversationMemory initialized for user: {user_id} with Mem0 cloud storage (Async)")
        else:
            self.memory_client = None
            logger.warning(f"ConversationMemory initialized in STATELESS mode for user: {user_id} (No Mem0 Key)")
    
    async def load_memory(self) -> List[Dict]:
        """Load all past conversations for this user from Mem0"""
        try:
            if not self.memory_client:
                logger.info("No Mem0 client - returning empty memory")
                return []

            # Get all memories for this user
            memories = await self.memory_client.get_all(user_id=self.user_id)
            
            conversations = []
            if memories:
                # Handle the results from Mem0 API
                results = memories.get('results', []) if isinstance(memories, dict) else []
                
                for memory in results:
                    # Extract metadata which contains our conversation info
                    metadata = memory.get('metadata', {})
                    if metadata:
                        conversations.append({
                            'memory_id': memory.get('id'),
                            'timestamp': metadata.get('timestamp'),
                            'message_count': metadata.get('message_count', 0),
                            'memory_text': memory.get('memory', ''),
                            'metadata': metadata
                        })
            
            logger.info(f"Loaded {len(conversations)} conversations from Mem0 for user {self.user_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"Error loading memory from Mem0: {e}")
            logger.exception("Full traceback:")
            return []
    
    async def save_conversation(self, conversation: Union[Dict, List, object]) -> Tuple[bool, str]:
        """Save a conversation to Mem0 cloud storage - returns (success, last_content)"""
        logger.info(f"save_conversation called for user {self.user_id}")
        
        last_content = ""
        
        try:
            # Convert conversation to dict/list if it's an object with model_dump method
            if hasattr(conversation, 'model_dump'):
                conversation_data = conversation.model_dump()
            else:
                conversation_data = conversation
            
            # Handle list format (array of conversation turns)
            if isinstance(conversation_data, list):
                all_messages = []
                # Extract all messages from all conversation turns
                for turn in conversation_data:
                    messages_in_turn = turn.get('messages', [])
                    all_messages.extend(messages_in_turn)
                
                # Use the latest timestamp
                latest_timestamp = max([turn.get('timestamp', 0) for turn in conversation_data if 'timestamp' in turn], default=None)
                timestamp = datetime.fromtimestamp(latest_timestamp).isoformat() if latest_timestamp else datetime.now().isoformat()
                
            # Handle dict format (single conversation)
            else:
                all_messages = conversation_data.get('messages', [])
                timestamp = conversation_data.get('timestamp')
                if not timestamp:
                    timestamp = datetime.now().isoformat()
                elif isinstance(timestamp, (int, float)):
                    timestamp = datetime.fromtimestamp(timestamp).isoformat()
            
            if not all_messages:
                logger.warning("No messages found in conversation, skipping save")
                return False, ""
            
            # Format messages for Mem0 - filter only user and assistant messages with actual content
            formatted_messages = []
            for msg in all_messages:
                msg_type = msg.get('type', 'message')
                role = msg.get('role', 'user')
                content = msg.get('content', [])
                
                # Skip non-message types
                if msg_type != 'message':
                    continue
                
                # Handle content
                if isinstance(content, list):
                    content_str = ' '.join([str(c) for c in content if c])
                else:
                    content_str = str(content) if content else ''
                
                if content_str and content_str.strip():
                    formatted_messages.append({
                        "role": role,
                        "content": content_str.strip()
                    })
                    last_content = content_str.strip()  # Keep track of last content
            
            if not formatted_messages:
                logger.warning("No valid messages with content to save")
                return False, ""
            
            logger.info(f"Formatted {len(formatted_messages)} messages for Mem0")
            logger.info(f"Latest message content preview: {last_content[:100]}...")
            
            # If no client (stateless mode), return success without saving
            if not self.memory_client:
                logger.info("Stateless mode - skipping Mem0 save")
                return True, last_content
            
            # Add memory to Mem0 (Async)
            result = await self.memory_client.add(
                messages=formatted_messages,
                user_id=self.user_id,
                metadata={
                    "timestamp": timestamp,
                    "message_count": len(formatted_messages),
                    "total_turns": len(conversation_data) if isinstance(conversation_data, list) else 1
                }
            )
            
            logger.info(f"Successfully saved conversation to Mem0 for user {self.user_id}")
            return True, last_content
            
        except Exception as e:
            logger.error(f"Error saving conversation to Mem0: {e}")
            logger.exception("Full traceback:")
            return False, ""
    
    async def get_recent_context(self, max_messages: int = 30) -> List[Dict]:
        """Get recent conversation context for the agent"""
        memory = await self.load_memory()
        all_messages = []
        
        for conversation in memory:
            if "messages" in conversation:
                all_messages.extend(conversation["messages"])
        
        recent_messages = all_messages[-max_messages:] if all_messages else []
        logger.info(f"Retrieved {len(recent_messages)} recent messages for user {self.user_id}")
        return recent_messages
    
    async def get_conversation_count(self) -> int:
        """Get total number of saved conversations"""
        memory = await self.load_memory()
        return len(memory)
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """Search through conversation memories using semantic search"""
        try:
            if not self.memory_client:
                return []
                
            results = await self.memory_client.search(
                query=query,
                user_id=self.user_id,
                limit=limit
            )
            logger.info(f"Found {len(results)} memories matching query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def get_all_memories(self) -> List[Dict]:
        """Get all memories for the user"""
        try:
            if not self.memory_client:
                return []
            memories = await self.memory_client.get_all(user_id=self.user_id)
            logger.info(f"Retrieved all memories for user {self.user_id}")
            return memories
        except Exception as e:
            logger.error(f"Error retrieving all memories: {e}")
            return []
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory by ID"""
        try:
            if not self.memory_client:
                return False
            await self.memory_client.delete(memory_id=memory_id)
            logger.info(f"Deleted memory {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False
    
    async def clear_all_memories(self) -> bool:
        """Clear all memories for this user"""
        try:
            if not self.memory_client:
                return False
            await self.memory_client.delete_all(user_id=self.user_id)
            logger.info(f"Cleared all memories for user {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing memories: {e}")
            return False