import logging
import asyncio
from telethon import events
from telethon.errors import UserPrivacyRestrictedError, UserNotMutualContactError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.phone import InviteToGroupCallRequest

logger = logging.getLogger(__name__)

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.inviteall'))
    async def invite_all(event):
        if not event.is_group:
            await event.edit("❌ This command only works in groups.")
            return

        await event.edit("⏳ gathering members to invite to VC...")
        
        chat = await event.get_chat()
        
        # This is strictly for VOICE CHATS (Group Calls) not simply adding to group.
        # However, Telethon doesn't have a direct "invite all to VC" helper that is easy to abuse without limits.
        # We need to get the InputUsers and invite them to the Call.
        
        try:
            # Get the full chat to find the call
            full_chat = await client.get_input_entity(chat)
            
            # This is complex because we need the Call object. 
            # Simplified approach: We assume the user wants to ADD members to the Group Call (Voice Chat).
            # But the user request says "Invite all group members to voice chat". 
            
            # NOTE: Inviting thousands of users is spammy and can get the account banned.
            # We will implement a safe version that iterates.
            
            # Ideally we need the 'call' object.
            # For now, let's implement a version that just simulates the 'Invite Members' generic logic,
            # but specific VC inviting requires the `phone.InviteToGroupCall` request.
            
            # Warning the user
            await event.edit("⚠️ Starting mass invite. This might take a while and risks account limits.")
            await asyncio.sleep(2)
            
            # Fetch participants
            # aggressive=True is needed for large groups to get all members
            await event.edit("⏳ Fetching members (this might take a few seconds)...")
            participants = await client.get_participants(chat, aggressive=True)
            
            await event.edit(f"✅ Found {len(participants)} total members. Filtering...")
            
            invited_count = 0
            
            # We need the call instance. 
            # Finding the active group call:
            # Finding the active group call:
            from telethon.tl.functions.phone import GetGroupCallRequest
            from telethon.tl.functions.channels import GetFullChannelRequest
            from telethon.tl.functions.messages import GetFullChatRequest
            
            if event.is_channel:
                full_chat = await client(GetFullChannelRequest(chat))
                call = full_chat.full_chat.call
            else:
                full_chat = await client(GetFullChatRequest(chat.id))
                call = full_chat.full_chat.call
            
            if not call:
                await event.edit("❌ No active voice chat found in this group.")
                return
            
            # Filter valid users
            users_to_invite = [
                user for user in participants 
                if not user.bot and not user.is_self
            ]
            
            total_u = len(users_to_invite)
            await event.edit(f"🚀 Found {total_u} users. Bombing invites... 💣")
            
            # Batch size for InviteToGroupCallRequest
            # Telegram usually accepts up to 100 users per request in some contexts, 
            # safe bet is 20-50 to avoid immediate errors, though flood wait is still a risk.
            BATCH_SIZE = 50
            
            for i in range(0, total_u, BATCH_SIZE):
                chunk = users_to_invite[i:i + BATCH_SIZE]
                try:
                    await client(InviteToGroupCallRequest(
                        call=call,
                        users=chunk
                    ))
                    invited_count += len(chunk)
                    await event.edit(f"🚀 Invited {invited_count}/{total_u} members...")
                    
                    # Small delay to allow server to process, but much faster than before
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"Batch failed: {e}")
            
            await event.edit(f"✅ Mission Complete! Invited {invited_count} members.")
            
        except Exception as e:
            logger.error(f"Error in inviteall: {e}")
            await event.edit(f"❌ Error: {e}")

    logger.info("Inviter plugin loaded!")
