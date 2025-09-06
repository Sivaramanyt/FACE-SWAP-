import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters
import logging

logging.basicConfig(level=logging.INFO)

# Environment variables
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Pyrogram client with stable connection settings
app = Client(
    "stable_face_swap",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=300,  # Increased from default 180
    workers=4,            # Reduced workers for stability
    max_concurrent_transmissions=2  # Limit concurrent operations
)

# Health check
async def health(request):
    return web.Response(text="✅ Bot Running")

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    print(f"📨 START from {message.from_user.id}")
    await message.reply("🤖 **Face Swap Bot Working!**\n\n✅ Connection stable on Koyeb!")

@app.on_message(filters.text & ~filters.command("start"))
async def echo_handler(client, message):
    print(f"📝 Message: {message.text}")
    await message.reply(f"Echo: {message.text}")

async def main():
    # Health server
    health_app = web.Application()
    health_app.router.add_get('/', health)
    runner = web.AppRunner(health_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8000)))
    await site.start()
    print("✅ Health server started")
    
    # Start bot with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await app.start()
            me = await app.get_me()
            print(f"✅ Bot @{me.username} connected successfully!")
            break
        except Exception as e:
            print(f"❌ Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(10)
            else:
                raise
    
    # Keep running with connection monitoring
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
    
