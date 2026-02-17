import logging
import json
import os
from telethon import events, functions, types

logger = logging.getLogger(__name__)

DATA_FILE = "user_reactor_data.json"

def load_data():
    """Load user reactor data from JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load user reactor data: {e}")
        return {}

def save_data(data):
    """Save user reactor data to JSON file."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save user reactor data: {e}")

def register(client):
    
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ur add (.+)'))
    async def add_user_react(event):
        """Add auto-reaction for a user in this group. Reply to their message with: .ur add <emoji>"""
        if not event.is_reply:
            await event.edit("❌ برای استفاده از این دستور باید به یک پیام ریپلای بزنی!\n\n**استفاده:** به پیام کاربر مورد نظر reply بزن و بنویس:\n`.ur add ❤️`")
            return
        
        # Get the group/chat ID
        chat_id = str(event.chat_id)
        
        # Get the replied message
        replied_msg = await event.get_reply_message()
        user_id = str(replied_msg.sender_id)
        
        # Get emoji from command
        emoji = event.pattern_match.group(1).strip()
        
        # Get user info for display
        try:
            user = await client.get_entity(int(user_id))
            user_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
            username_display = f"@{user.username}" if user.username else user_name
        except:
            username_display = f"User {user_id}"
        
        # Get chat info
        try:
            chat = await client.get_entity(int(chat_id))
            chat_name = chat.title if hasattr(chat, 'title') else "این چت"
        except:
            chat_name = f"Chat {chat_id}"
        
        # Load data
        data = load_data()
        
        # Initialize chat if not exists
        if chat_id not in data:
            data[chat_id] = {}
        
        # Add/update user reaction
        data[chat_id][user_id] = emoji
        save_data(data)
        
        await event.edit(
            f"✅ **ریکشن تنظیم شد!**\n\n"
            f"👤 کاربر: {username_display}\n"
            f"💬 گروه: {chat_name}\n"
            f"😊 ریکشن: {emoji}\n\n"
            f"از این به بعد به همه پیام‌های این کاربر در این گروه ریکشن {emoji} میره."
        )
    
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ur del$'))
    async def del_user_react(event):
        """Delete auto-reaction for a user. Reply to their message with: .ur del"""
        if not event.is_reply:
            await event.edit("❌ برای حذف ریکشن باید به یک پیام از کاربر مورد نظر ریپلای بزنی!\n\n**استفاده:** به پیامش reply بزن و بنویس:\n`.ur del`")
            return
        
        chat_id = str(event.chat_id)
        replied_msg = await event.get_reply_message()
        user_id = str(replied_msg.sender_id)
        
        data = load_data()
        
        if chat_id in data and user_id in data[chat_id]:
            del data[chat_id][user_id]
            
            # Clean up empty chats
            if not data[chat_id]:
                del data[chat_id]
            
            save_data(data)
            await event.edit("🗑 **ریکشن حذف شد!**\n\nدیگه به پیام‌های این کاربر در این گروه ریکشن نمیره.")
        else:
            await event.edit("❌ برای این کاربر در این گروه ریکشنی تنظیم نشده!")
    
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ur list$'))
    async def list_user_react(event):
        """List all user reactions in this group."""
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data or not data[chat_id]:
            await event.edit("📭 **هیچ ریکشنی در این گروه تنظیم نشده!**\n\nبرای افزودن ریکشن:\nبه پیام کاربر مورد نظر reply بزن و بنویس:\n`.ur add ❤️`")
            return
        
        # Get chat name
        try:
            chat = await client.get_entity(int(chat_id))
            chat_name = chat.title if hasattr(chat, 'title') else "این چت"
        except:
            chat_name = f"Chat {chat_id}"
        
        msg = f"📋 **لیست ریکشن‌ها در {chat_name}:**\n\n"
        
        for user_id, emoji in data[chat_id].items():
            try:
                user = await client.get_entity(int(user_id))
                user_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
                username_display = f"@{user.username}" if user.username else user_name
            except:
                username_display = f"User {user_id}"
            
            msg += f"👤 {username_display} ➡️ {emoji}\n"
        
        await event.edit(msg)
    
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ur clear$'))
    async def clear_user_react(event):
        """Clear all user reactions in this group."""
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id in data:
            count = len(data[chat_id])
            del data[chat_id]
            save_data(data)
            await event.edit(f"🗑 **تمیز شد!**\n\n{count} ریکشن از این گروه حذف شد.")
        else:
            await event.edit("📭 هیچ ریکشنی در این گروه تنظیم نشده!")
    
    # Main handler: Auto-react to messages from specific users
    @client.on(events.NewMessage)
    async def auto_react_handler(event):
        """Automatically react to messages from specified users."""
        try:
            # Skip outgoing messages
            if event.out:
                return
            
            chat_id = str(event.chat_id)
            user_id = str(event.sender_id)
            
            data = load_data()
            
            # Check if this chat has any reactions set
            if chat_id not in data:
                return
            
            # Check if this user has a reaction set in this chat
            if user_id not in data[chat_id]:
                return
            
            emoji = data[chat_id][user_id]
            
            # Send reaction
            try:
                await client(functions.messages.SendReactionRequest(
                    peer=event.chat_id,
                    msg_id=event.id,
                    reaction=[types.ReactionEmoji(emoticon=emoji)]
                ))
                logger.info(f"User Reactor: Reacted {emoji} to message from user {user_id} in chat {chat_id}")
            except Exception as e:
                logger.error(f"User Reactor: Failed to send reaction: {e}")
        
        except Exception as e:
            logger.error(f"Error in user reactor handler: {e}")
    
    logger.info("User Reactor plugin loaded!")
