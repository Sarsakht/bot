import logging
import json
import os
from telethon import events

logger = logging.getLogger(__name__)

REACT_FILE = "reactor_data.json"

def load_reacts():
    if not os.path.exists(REACT_FILE):
        return {}
    with open(REACT_FILE, 'r') as f:
        return json.load(f)

def save_reacts(data):
    with open(REACT_FILE, 'w') as f:
        json.dump(data, f)

def register(client):
    # Short alias: .r add <key> <emoji>
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.r add (\w+) (.+)'))
    async def add_react(event):
        keyword = event.pattern_match.group(1)
        emoji = event.pattern_match.group(2)
        
        data = load_reacts()
        data[keyword] = emoji
        save_reacts(data)
        
        await event.edit(f"✅ **Set:** `{keyword}` ➡️ {emoji}")

    # Reply mode: Reply to a message with ".r add <emoji>" to use that message's text as keyword? 
    # Or maybe simpler: just simplified commands.

    @client.on(events.NewMessage(outgoing=True, pattern=r'\.r del (\w+)'))
    async def del_react(event):
        keyword = event.pattern_match.group(1)
        
        data = load_reacts()
        if keyword in data:
            del data[keyword]
            save_reacts(data)
            await event.edit(f"🗑 **Deleted:** `{keyword}`")
        else:
            await event.edit(f"❌ Not found: `{keyword}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r'\.r list'))
    async def list_react(event):
        data = load_reacts()
        if not data:
            await event.edit("📭 No reactions set.")
            return
            
        msg = "📋 **Auto-Reactions List:**\n\n"
        for k, v in data.items():
            msg += f"🔹 `{k}` ➡️ {v}\n"
        await event.edit(msg)

    # Legacy support (keeping old commands but hidden or optional)
    # New handler for checking messages
    from telethon import functions, types

    # Handler for checking messages
    @client.on(events.NewMessage)
    async def handler(event):
        # logger.info(f"Reactor checking message: {event.id}") 
        try:
            try:
                data = load_reacts()
            except Exception as e:
                logger.error(f"Reactor: Data load error: {e}")
                return
            
            if not data:
                return

            text = event.raw_text.lower()
            if not text:
                return
            
            # logger.info(f"Reactor checking text: '{text[:10]}...' against {len(data)} keywords")

            for keyword, emoji in data.items():
                if keyword.lower() in text:
                    logger.info(f"Reactor: MATCH! '{keyword}' found. Sending {emoji}")
                    try:
                        # Use raw API call for maximum compatibility
                        await client(functions.messages.SendReactionRequest(
                            peer=event.chat_id,
                            msg_id=event.id,
                            reaction=[types.ReactionEmoji(emoticon=emoji)]
                        ))
                        logger.info("Reactor: Reaction sent successfully.")
                    except Exception as e:
                        logger.error(f"Reactor: Failed to react: {e}")
                    break
        except Exception as e:
            logger.error(f"Error in reactor handler: {e}")

    logger.info("Reactor plugin loaded!")
