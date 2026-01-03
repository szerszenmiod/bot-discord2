import discord, aiosqlite
from discord.ext import commands
from utils.permissions import has_support_role
from utils.transcript import save_transcript

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def close(self, ctx):
        row = await (await aiosqlite.connect("data/bot.db").execute(
            "SELECT user_id FROM tickets WHERE channel_id=?", (ctx.channel.id,)
        )).fetchone()
        if not row:
            return await ctx.respond("To nie jest kanał ticketa.")

        path = await save_transcript(ctx.channel)
        await aiosqlite.connect("data/bot.db").execute(
            """UPDATE tickets SET closed_at=datetime('now'), closed_by=?, status='close',
               transcript_path=? WHERE channel_id=?""",
            (ctx.author.id, path, ctx.channel.id),
        )
        await ctx.respond("Transcript zapisany. Kanał zniknie za 5 sekund...")
        await asyncio.sleep(5)
        await ctx.channel.delete()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def blacklistadd(self, ctx, user: discord.User, reason: str = "brak"):
        async with aiosqlite.connect("data/bot.db") as db:
            await db.execute("INSERT OR IGNORE INTO blacklisted(user_id) VALUES(?)", (user.id,))
            await db.commit()
        await ctx.respond(f"{user.display_name} został zablokowany.")

def setup(bot):
    bot.add_cog(AdminCog(bot))
