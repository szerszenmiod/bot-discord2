"""
Enterprise Ticket Bot – Python 3.11+
Author: @Kimi
"""
import asyncio, logging, sys, json, aiosqlite
import discord
from discord.ext import commands

with open("config.json", encoding="utf-8") as f:
    CONFIG = json.load(f)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s – %(name)s – %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

class TicketBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=CONFIG["bot"]["status"]["text"],
            ),
        )

    async def setup_hook(self):
        async with aiosqlite.connect("data/bot.db") as db:
            await db.executescript(
                """
CREATE TABLE IF NOT EXISTS tickets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER,
    user_id  INTEGER,
    channel_id INTEGER,
    category TEXT,
    opened_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME,
    closed_by INTEGER,
    status TEXT DEFAULT 'open',
    transcript_path TEXT
);

CREATE TABLE IF NOT EXISTS blacklisted(
    user_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS staff_stats(
    user_id INTEGER PRIMARY KEY,
    closed_count INTEGER DEFAULT 0
);
            """
            )
            await db.commit()

        for cog in ("ticket", "admin", "logs", "blacklist", "stats"):
            await self.load_extension(f"cogs.{cog}_cog")
            logging.info(f"[COG] Loaded {cog}")

    async def on_ready(self):
        logging.info(f"🟢 {self.user} ready!")


bot = TicketBot()
bot.run(CONFIG["bot"]["token"])
