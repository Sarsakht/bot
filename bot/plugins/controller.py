from telethon import events, Button
import config
from plugins.reactor import load_reacts, save_reacts
import logging

logger = logging.getLogger(__name__)

# State management
# {user_id: {"state": "STATE_NAME", "data": {...}}}
user_states = {}

# Constants
STATE_IDLE = "IDLE"
STATE_WAITING_REACT_KEYWORD = "WAITING_REACT_KEYWORD"
STATE_WAITING_REACT_EMOJI = "WAITING_REACT_EMOJI"

async def get_state(user_id):
    return user_states.get(user_id, {"state": STATE_IDLE})

async def set_state(user_id, state, data=None):
    if data is None:
        data = {}
    user_states[user_id] = {"state": state, "data": data}

def register_bot(bot):
    
    # --- Inline Query Handler ---
    @bot.on(events.InlineQuery)
    async def inline_handler(event):
        builder = event.builder
        sender_id = event.sender_id

        if config.OWNER_ID and sender_id != config.OWNER_ID:
            await event.answer([builder.article(
                "Access Denied",
                text="⛔ شما دسترسی به این بات را ندارید.",
            )])
            return

        buttons = [
            [Button.inline("🎭 تنظیمات ری‌اکشن", b"menu_reactor")],
            [Button.inline("⚙️ تنظیمات عمومی", b"menu_general")]
        ]
        
        await event.answer([builder.article(
            "Control Panel",
            text="👋 **پنل مدیریت ربات**\nجهت دسترسی به تنظیمات از منوی زیر استفاده کنید:",
            buttons=buttons
        )])

    @bot.on(events.NewMessage(pattern="/start"))
    async def start_handler(event):
        sender_id = event.sender_id
        
        # Security check (optional, but good for self-bot controllers)
        if config.OWNER_ID and sender_id != config.OWNER_ID:
            await event.reply("⛔ شما دسترسی به این بات را ندارید.")
            return

        buttons = [
            [Button.inline("🎭 تنظیمات ری‌اکشن", b"menu_reactor")],
            [Button.inline("⚙️ تنظیمات عمومی", b"menu_general")]
        ]
        
        await event.reply("👋 سلام! به پنل مدیریت ربات خوش آمدید.\nلطفا یکی از گزینه‌های زیر را انتخاب کنید:", buttons=buttons)
        await set_state(sender_id, STATE_IDLE)

    @bot.on(events.CallbackQuery(pattern=b"menu_main"))
    async def menu_main(event):
        buttons = [
            [Button.inline("🎭 تنظیمات ری‌اکشن", b"menu_reactor")],
            [Button.inline("⚙️ تنظیمات عمومی", b"menu_general")]
        ]
        await event.edit("منوی اصلی:", buttons=buttons)
        await set_state(event.sender_id, STATE_IDLE)

    # --- General Menu ---
    @bot.on(events.CallbackQuery(pattern=b"menu_general"))
    async def menu_general(event):
        buttons = [
            [Button.inline("🔄 وضعیت ربات", b"gen_status"), Button.inline("🏓 پینگ", b"gen_ping")],
            [Button.inline("🔙 بازگشت", b"menu_main")]
        ]
        await event.edit("⚙️ **تنظیمات عمومی**", buttons=buttons)

    @bot.on(events.CallbackQuery(pattern=b"gen_ping"))
    async def gen_ping(event):
        await event.answer("Pong! 🏓", alert=True)

    @bot.on(events.CallbackQuery(pattern=b"gen_status"))
    async def gen_status(event):
        await event.answer("✅ ربات فعال است.", alert=True)

    # --- Reactor Menu ---
    @bot.on(events.CallbackQuery(pattern=b"menu_reactor"))
    async def menu_reactor(event):
        buttons = [
            [Button.inline("➕ افزودن واکنش", b"react_add"), Button.inline("🗑 حذف واکنش", b"react_del")],
            [Button.inline("📋 لیست واکنش‌ها", b"react_list")],
            [Button.inline("🔙 بازگشت", b"menu_main")]
        ]
        await event.edit("🎭 **تنظیمات ری‌اکشن**\nچه کاری می‌خواهید انجام دهید؟", buttons=buttons)

    @bot.on(events.CallbackQuery(pattern=b"react_list"))
    async def react_list(event):
        data = load_reacts()
        if not data:
            msg = "📭 لیست خالی است."
        else:
            msg = "📋 **لیست واکنش‌های خودکار:**\n\n"
            for k, v in data.items():
                msg += f"🔹 `{k}` ➡️ {v}\n"
        
        buttons = [[Button.inline("🔙 بازگشت", b"menu_reactor")]]
        await event.edit(msg, buttons=buttons)

    @bot.on(events.CallbackQuery(pattern=b"react_add"))
    async def react_add(event):
        # Force private chat for input
        chat = await event.get_chat()
        # event.is_private can be tricky with inline messages depending on telethon version context, 
        # but checking chat type is safer if needed. However, sender_id logic applies.
        # If it's an inline message, the 'chat' is the chat where it was sent.
        
        # A simple check: if we are in an inline query result message in a group, we can't easily get text input.
        # We'll just ask them to go to private.
        try:
             # This is a bit hacky to detect if we are in a proper private chat with the bot
             # If event.chat_id is the user's ID, it's private.
             if event.chat_id != event.sender_id:
                 await event.answer("❌ برای افزودن موارد لطفا به پیوی ربات بیایید.", alert=True)
                 return
        except:
             # Fallback if chat_id access fails implementation specific
             pass

        await event.edit("✍️ لطفاً **کلمه کلیدی** یا متنی که می‌خواهید به آن واکنش نشان دهم را ارسال کنید.\n\n(برای لغو /cancel را بزنید)")
        await set_state(event.sender_id, STATE_WAITING_REACT_KEYWORD)

    @bot.on(events.CallbackQuery(pattern=b"react_del"))
    async def react_del_menu(event):
        data = load_reacts()
        if not data:
            await event.answer("لیست خالی است!", alert=True)
            return

        # Create buttons for each keyword to delete easily
        buttons = []
        row = []
        for k in list(data.keys())[:20]: # Limit to 20 to avoid confusing lists
            row.append(Button.inline(f"❌ {k}", f"do_del_{k}".encode()))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
            
        buttons.append([Button.inline("🔙 بازگشت", b"menu_reactor")])
        await event.edit("🗑 برای حذف، روی کلمه مورد نظر کلیک کنید:", buttons=buttons)

    @bot.on(events.CallbackQuery(pattern=b"do_del_(.+)"))
    async def do_del(event):
        keyword = event.pattern_match.group(1).decode()
        data = load_reacts()
        if keyword in data:
            del data[keyword]
            save_reacts(data)
            await event.answer(f"حذف شد: {keyword}", alert=True)
            # Refresh list
            await react_del_menu(event)
        else:
            await event.answer("یافت نشد.", alert=True)

    # --- Message Handler for Inputs ---
    @bot.on(events.NewMessage())
    async def input_handler(event):
        sender_id = event.sender_id
        
        # Only accept inputs in private chat with the bot
        if not event.is_private:
            return

        current = await get_state(sender_id)
        state = current["state"]
        
        if event.text == "/cancel":
            await event.reply("❌ عملیات لغو شد.", buttons=[[Button.inline("🔙 منوی اصلی", b"menu_main")]])
            await set_state(sender_id, STATE_IDLE)
            return

        if state == STATE_WAITING_REACT_KEYWORD:
            keyword = event.text
            # Save keyword and ask for emoji
            await set_state(sender_id, STATE_WAITING_REACT_EMOJI, {"keyword": keyword})
            
            # Show emoji keyboard
            emojis = ["👍", "❤️", "😂", "😮", "😢", "🔥", "🤝", "👀", "🍌", "💩"]
            buttons = []
            row = []
            for em in emojis:
                row.append(Button.inline(em, f"set_react_{em}".encode()))
                if len(row) == 5:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            
            await event.reply(f"✅ کلمه دریافت شد: `{keyword}`\nحالا **واکنش** مورد نظر را انتخاب کنید:", buttons=buttons)
            
        elif state == STATE_IDLE:
            # Ignore random messages or handle commands
            pass

    @bot.on(events.CallbackQuery(pattern=b"set_react_(.+)"))
    async def set_react(event):
        emoji = event.pattern_match.group(1).decode()
        sender_id = event.sender_id
        current = await get_state(sender_id)
        
        if current["state"] == STATE_WAITING_REACT_EMOJI:
            keyword = current["data"]["keyword"]
            
            data = load_reacts()
            data[keyword] = emoji
            save_reacts(data)
            
            await event.edit(f"✅ **ثبت شد!**\n\n🔹 کلمه: `{keyword}`\n🔹 واکنش: {emoji}", buttons=[[Button.inline("🔙 بازگشت", b"menu_reactor")]])
            await set_state(sender_id, STATE_IDLE)
        else:
            await event.answer("خطا: وضعیت نامعتبر.", alert=True)

