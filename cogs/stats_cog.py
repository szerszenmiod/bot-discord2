"""
Statystyki ticketów / leaderboard
"""
from discord.ext import commands
import aiosqlite
import discord


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="stats", description="Statystyki ticketów")
    async def stats(self, ctx):
        async with aiosqlite.connect("data/bot.db") as db:
            cur = await db.execute("SELECT COUNT(*) FROM tickets")
            total = await cur.fetchone()

            cur = await db.execute("SELECT COUNT(*) FROM tickets WHERE status='close'")
            closed = await cur.fetchone()

            cur = await db.execute(
                "SELECT user_id, closed_count FROM staff_stats ORDER BY closed_count DESC LIMIT 10"
            )
            board = await cur.fetchall()

        embed = discord.Embed(
            title="📊 Statystyki Globalne",
            description=f"• Razem ticketów: **{total[0]}**\n"
                        f"• Zamkniętych: **{closed[0]}**\n\n"
                        f"👑 Leaderboard top 10:",
            color=0xf39c12,
        )
        for idx, (uid, cnt) in enumerate(board, 1):
            user = self.bot.get_user(uid) or f"<@{uid}>"
            embed.add_field(name=f"{idx}. {user}", value=f"{cnt} zamknięć", inline=False)

        await ctx.respond(embed=embed)

    @commands.slash_command(name="staffstats")
    @commands.has_permissions(manage_channels=True)
    async def staffstats(self, ctx, member: discord.User):
        async with aiosqlite.connect("data/bot.db") as db:
            cur = await db.execute(
                "SELECT closed_count FROM staff_stats WHERE user_id=?", (member.id,)
            )
            row = await cur.fetchone()
        count = row[0] if row else 0
        await ctx.respond(f"👤 **{member.display_name}** zamknął(a) `{count}` ticketów.")

    @staticmethod
    async def inc_closed(user_id: int):
        async with aiosqlite.connect("data/bot.db") as db:
            await db.execute(
                "INSERT INTO staff_stats(user_id, closed_count) VALUES(?,1) "
                "ON CONFLICT(user_id) DO UPDATE SET closed_count=closed_count+1",
                (user_id,),
            )
            await db.commit()


def setup(bot):
    bot.add_cog(StatsCog(bot))
