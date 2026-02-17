import logging
import json
import os
from telethon import events

logger = logging.getLogger(__name__)

DATA_FILE = "autoreply_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.addreply (\w+) (.+)'))
    async def add_reply(event):
        keyword = event.pattern_match.group(1)
        response = event.pattern_match.group(2)
        
        data = load_data()
        data[keyword] = response
        save_data(data)
        
        await event.edit(f"✅ Auto-reply added: `{keyword}` -> `{response}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r'\.delreply (\w+)'))
    async def del_reply(event):
        keyword = event.pattern_match.group(1)
        
        data = load_data()
        if keyword in data:
            del data[keyword]
            save_data(data)
            await event.edit(f"✅ Auto-reply deleted: `{keyword}`")
        else:
            await event.edit(f"❌ Keyword `{keyword}` not found.")

    @client.on(events.NewMessage(outgoing=True, pattern=r'\.listreply'))
    async def list_reply(event):
        data = load_data()
        if not data:
            await event.edit("No auto-replies set.")
            return
            
        msg = "**Auto-Replies:**\n"
        for k, v in data.items():
            msg += f"- `{k}`: `{v}`\n"
        await event.edit(msg)

    # Cache own ID
    MY_ID = None

    @client.on(events.NewMessage)
    async def handler(event):
        try:
            nonlocal MY_ID
            if MY_ID is None:
                try:
                    me = await client.get_me()
                    if me:
                        MY_ID = me.id
                except:
                    pass

            # Don't reply to yourself
            if event.out or (MY_ID and event.sender_id == MY_ID): 
                return
            
            # ... rest of logic
            try:
                data = load_data()
            except (json.JSONDecodeError, OSError):
                return
            
            if not data:
                return

            text = event.raw_text.lower()
            if not text:
                return
            
            for keyword, response in data.items():
                if keyword.lower() in text:
                    await event.reply(response)
                    logger.info(f"Replied to '{keyword}' with '{response}'")
                    break
        except Exception as e:
            logger.error(f"Error in autoreply: {e}")

    logger.info("AutoReply plugin loaded!")
