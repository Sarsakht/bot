import logging
import os
from telethon import events
from telethon.tl import functions
import asyncio

logger = logging.getLogger(__name__)

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.(setprofile|setprof)'))
    async def setprofile_handler(event):
        try:
            if not event.is_reply:
                await event.edit("❌ لطفا روی یک عکس یا ویدیو ریپلای کنید.")
                await asyncio.sleep(3)
                await event.delete()
                return
            
            replied_msg = await event.get_reply_message()
            
            if not replied_msg.media:
                await event.edit("❌ پیام ریپلای شده باید عکس یا ویدیو باشد.")
                await asyncio.sleep(3)
                await event.delete()
                return
            
            is_photo = replied_msg.photo is not None
            is_video = replied_msg.video is not None or replied_msg.gif is not None
            
            if is_photo:
                await event.edit("**در حال دانلود عکس .**")
                await asyncio.sleep(0.3)
                await event.edit("**در حال دانلود عکس ..**")
                await asyncio.sleep(0.3)
                await event.edit("**در حال دانلود عکس ...**")
                
                os.makedirs("downloads", exist_ok=True)
                file_path = await replied_msg.download_media("downloads/")
                
                await event.edit("**در حال تنظیم پروفایل ..**")
                
                uploaded = await client.upload_file(file_path)
                await client(functions.photos.UploadProfilePhotoRequest(
                    file=uploaded
                ))
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                await event.edit("✅ **پروفایل با موفقیت تنظیم شد!** 👁")
                await asyncio.sleep(5)
                await event.delete()
                
            elif is_video:
                await event.edit("**در حال دانلود ویدیو .**")
                await asyncio.sleep(0.3)
                await event.edit("**در حال دانلود ویدیو ..**")
                await asyncio.sleep(0.3)
                await event.edit("**در حال دانلود ویدیو ...**")
                
                os.makedirs("downloads", exist_ok=True)
                file_path = await replied_msg.download_media("downloads/")
                
                await event.edit("**در حال تنظیم پروفایل ..**")
                
                uploaded = await client.upload_file(file_path)
                await client(functions.photos.UploadProfilePhotoRequest(
                    video=uploaded
                ))
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                await event.edit("✅ **پروفایل ویدیویی با موفقیت تنظیم شد!** 👁")
                await asyncio.sleep(5)
                await event.delete()
            else:
                await event.edit("❌ فقط عکس یا ویدیو پشتیبانی می‌شود.")
                await asyncio.sleep(3)
                await event.delete()
                
        except Exception as e:
            logger.error(f"Error in setprofile: {e}")
            await event.edit(f"❌ خطا: {str(e)}")
            await asyncio.sleep(5)
            await event.delete()

    logger.info("SetProfile plugin loaded!")
