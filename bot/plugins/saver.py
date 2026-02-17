import logging
from telethon import events, types

logger = logging.getLogger(__name__)

def register(client):
    @client.on(events.NewMessage)
    async def handler(event):
        try:
            msg = event.message
            if not msg or not msg.media:
                return

            # Check for timed media in multiple ways
            is_timed = False
            ttl_value = None
            
            # Method 1: Check message.ttl_seconds
            if hasattr(msg, 'ttl_seconds') and msg.ttl_seconds and msg.ttl_seconds > 0:
                is_timed = True
                ttl_value = msg.ttl_seconds
                logger.info(f"Saver: Found TTL on message: {ttl_value}s")
            
            # Method 2: Check media.ttl_seconds (for photos/videos)
            if hasattr(msg.media, 'ttl_seconds') and msg.media.ttl_seconds and msg.media.ttl_seconds > 0:
                is_timed = True
                ttl_value = msg.media.ttl_seconds
                logger.info(f"Saver: Found TTL on media: {ttl_value}s")
            
            # Method 3: Check for MessageMediaPhoto with ttl_seconds
            if isinstance(msg.media, types.MessageMediaPhoto):
                if hasattr(msg.media.photo, 'ttl_seconds') and msg.media.photo.ttl_seconds:
                    is_timed = True
                    ttl_value = msg.media.photo.ttl_seconds
                    logger.info(f"Saver: Found TTL on photo: {ttl_value}s")
            
            # Method 4: Check for MessageMediaDocument with ttl_seconds  
            if isinstance(msg.media, types.MessageMediaDocument):
                if hasattr(msg.media.document, 'ttl_seconds') and msg.media.document.ttl_seconds:
                    is_timed = True
                    ttl_value = msg.media.document.ttl_seconds
                    logger.info(f"Saver: Found TTL on document: {ttl_value}s")
            
            if is_timed:
                logger.info(f"Saver: DETECTED TIMED/VIEW-ONCE MEDIA! TTL: {ttl_value}s")
                
                try:
                    logger.info("Saver: Attempting download...")
                    path = await msg.download_media()
                    
                    if path:
                        logger.info(f"Saver: Downloaded to {path}")
                        
                        # Send to Saved Messages
                        sender_name = "Unknown"
                        try:
                            sender = await event.get_sender()
                            sender_name = sender.first_name if sender else "Unknown"
                        except:
                            pass
                        
                        await client.send_file(
                            "me", 
                            path, 
                            caption=f"🔥 Saved View-Once Media\n👤 From: {sender_name}\n⏱ TTL: {ttl_value}s"
                        )
                        logger.info("Saver: Successfully saved to Saved Messages")
                        
                        # Cleanup
                        import os
                        if os.path.exists(path):
                            os.remove(path)
                    else:
                        logger.error("Saver: Download returned None - media might be protected")
                        
                except Exception as e:
                    logger.error(f"Saver: Failed to save media: {e}")

        except Exception as e:
            logger.error(f"Saver: Unexpected error: {e}")

    logger.info("Saver plugin loaded!")
