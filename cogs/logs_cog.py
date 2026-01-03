"""
logging / audit ticketa
"""
import discord
from discord.ext import commands
import aiosqlite
from utils.embeds import ticket_embed


class LogsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # wskazówki z config.json
        with open("config.json") as f:
            self.cfg = __import__("json").load(f)
        self.ticket_log = self.cfg['logs']['ticket']
        self.admin_log = self.cfg['logs']['admin']
        self.error_log = self.cfg['logs']['error']

    # --- hooks: to jest uruchamiane przez inne cogi  -----------------
    async def dispatch_ticket_open(self, channel, user, category):
        embed = ticket_embed(
            "📂 Ticket otworzony",
            f"• Użytkownik: {user} (`{user.id}`)\n"
            f"• Kategoria: **{category}**\n"
            f"• Kanał: {channel.mention}",
            0x2ecc71,
        )
        lg_ch = self.bot.get_channel(self.ticket_log)
        if lg_ch:
            await lg_ch.send(embed=embed)

    async def dispatch_ticket_close(self, channel_id, closer, transcript_path):
        async with aiosqlite.connect("data/bot.db") as db:
            cur = await db.execute(
                "SELECT user_id, category FROM tickets WHERE channel_id=?",
                (channel_id,),
            )
            row = await cur.fetchone()
            if not row:
                return
            user_id, category = row

        user = await self.bot.fetch_user(user_id)
        embed = ticket_embed(
            "🔒 Ticket zamknięty",
            f"• Zamknięty przez: {closer} (`{closer.id}`)\n"
            f"• Użytkownik: {user} (`{user.id}`)\n"
            f"• Kategoria: **{category}**",
            0xe74c3c,
        )
        lg_ch = self.bot.get_channel(self.ticket_log)
        if lg_ch:
            try:
                await lg_ch.send(embed=embed, file=discord.File(transcript_path))
            except:
                await lg_ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        embed = discord.Embed(
            title="🛠 Błąd bota",
            description=str(error),
            color=0xff0000,
        )
        ch = self.bot.get_channel(self.error_log)
        if ch:
            await ch.send(embed=embed)
        else:
            print("[ERROR] w/o target channel:", error)


def setup(bot):
    bot.add_cog(LogsCog(bot))
