import logging
from telethon import events, utils

logger = logging.getLogger(__name__)

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.pvs(?: (.+))?'))
    async def pvs_handler(event):
        args = event.pattern_match.group(1)
        
        limit = 200 # Default
        if args:
            if args.lower() == "all":
                limit = None
            elif args.isdigit():
                limit = int(args)
        
        limit_str = "All" if limit is None else str(limit)
        msg = await event.edit(f"🔄 **Calculating Stats...**\nScanning {limit_str} most recent dialogs.\n(Use `.pvs all` to scan everything)")
        
        try:
            # List to store (count, name, entity)
            stats = []
            
            dialog_count = 0
            async for dialog in client.iter_dialogs(limit=limit):
                if dialog.is_user and not dialog.entity.bot and not dialog.entity.is_self:
                    try:
                        # Get total message count
                        total = (await client.get_messages(dialog.input_entity, limit=0)).total
                        
                        name = utils.get_display_name(dialog.entity)
                        stats.append((total, name, dialog.entity.id))
                        dialog_count += 1
                        
                        # Update progress every 20 chats
                        if dialog_count % 20 == 0:
                            await msg.edit(f"🔄 Scanning... ({dialog_count} chats checked)\nFound: {name} ({total})")
                            
                    except Exception as e:
                        logger.warning(f"Failed to get stats for {dialog.name}: {e}")
            
            # Sort by count descending
            stats.sort(key=lambda x: x[0], reverse=True)
            
            # Get top 10 (increased from 5)
            top_list = stats[:10]
            
            output = f"🏆 **Top Private Chats** (checked {dialog_count} dialogs)\n\n"
            
            ranks = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            
            for i, (count, name, user_id) in enumerate(top_list):
                rank = ranks[i] if i < len(ranks) else f"#{i+1}"
                output += f"{rank} **{name}**: `{count:,}` msgs\n"
            
            if not top_list:
                output = "📭 No private chats found with messages."
                
            await msg.edit(output)
            
        except Exception as e:
            logger.error(f"Error in pvs plugin: {e}")
            await msg.edit(f"❌ Error calculating stats: {e}")

    logger.info("Stats plugin loaded!")
