import logging
import os
import platform
import time
from telethon import events

logger = logging.getLogger(__name__)

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.panel'))
    async def panel(event):
        try:
            # System info
            uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - client._start_time)) if hasattr(client, '_start_time') else "N/A"
            ping = f"{client.ping_delay:.0f}ms" if hasattr(client, 'ping_delay') else "N/A"
            
            msg = f"""
**🕹 CONTROL PANEL**
━━━━━━━━━━━━━━━━━━
📊 **Status:** Online
⚡ **Ping:** `{ping}`
⏱ **Uptime:** `{uptime}`
━━━━━━━━━━━━━━━━━━

**⚙️ Modules & Commands:**

**🚀 Auto-Reactions**
• `.r add <word> <emoji>` : Add reaction
• `.r del <word>` : Delete reaction
• `.r list` : List all

**🎙 Voice Inviter**
• `.inviteall` : 💣 Mass Invite to VC

**🤖 Auto-Reply**
• `.addreply <word> <msg>`
• `.delreply <word>`
• `.listreply`

**📸 Media Saver**
• *Active (Auto-save timed media)*

━━━━━━━━━━━━━━━━━━
"""
            await event.edit(msg)
        except Exception as e:
            await event.edit(f"❌ Panel Error: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'\.ping'))
    async def ping(event):
        s = time.time()
        await event.edit("Checking...")
        d = time.time() - s
        await event.edit(f"📶 **Pong!** `{d*1000:.2f}ms`")

    # Hook to capture start time
    if not hasattr(client, '_start_time'):
        client._start_time = time.time()
        
    logger.info("Enhanced Manager loaded!")
