# main.py
import logging
import sys
import os
from telethon import TelegramClient, events
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the client
if not os.path.exists("sessions"):
    os.makedirs("sessions")

client = TelegramClient(
    f"sessions/{config.SESSION_NAME}",
    config.API_ID,
    config.API_HASH
)

bot_client = TelegramClient(
    f"sessions/bot_controller",
    config.API_ID,
    config.API_HASH
)

def load_plugins():
    plugin_dir = "plugins"
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
        
    # List all .py files in plugins directory
    plugins = [f[:-3] for f in os.listdir(plugin_dir) if f.endswith(".py") and f != "__init__.py"]
    
    for plugin in plugins:
        try:
            # Import the plugin module
            module_name = f"{plugin_dir}.{plugin}"
            __import__(module_name)
            module = sys.modules[module_name]
            
            # Check if the module has a 'register' function
            if hasattr(module, 'register'):
                module.register(client)
                logger.info(f"Loaded plugin (User): {plugin}")
            
            # Check if the module has a 'register_bot' function
            if hasattr(module, 'register_bot'):
                module.register_bot(bot_client)
                logger.info(f"Loaded plugin (Bot): {plugin}")
                
            if not hasattr(module, 'register') and not hasattr(module, 'register_bot'):
                logger.warning(f"Plugin {plugin} has no 'register' or 'register_bot' function.")
                
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin}: {e}")

async def main():
    logger.info("Starting bot...")
    
    # Load plugins
    load_plugins()
    
    await client.start()
    
    if config.BOT_TOKEN and config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        await bot_client.start(bot_token=config.BOT_TOKEN)
        logger.info("Controller Bot is running!")
    else:
        logger.warning("BOT_TOKEN not set in config.py. Controller Bot will not start.")
        
    logger.info("Userbot is running!")
    
    import asyncio
    
    tasks = [client.run_until_disconnected()]
    
    if config.BOT_TOKEN and config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        tasks.append(bot_client.run_until_disconnected())
        
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    client.loop.run_until_complete(main())
