"""
System blacklisty
"""
from discord.ext import commands
import aiosqlite
import discord


class BlacklistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="blacklist", description="Zarządzanie czarną listą")
    async def blacklist_cmd(self, ctx):
        ...

    @blacklist_cmd.sub_command(name="add")
    async def bl_add(self, ctx, user: discord.User, *, powod: str = "nie podano"):
        async with aiosqlite.connect("data/bot.db") as db:
            await db.execute(
                "INSERT OR IGNORE INTO blacklisted(user_id) VALUES(?)", (user.id,)
            )
            await db.commit()
        await ctx.respond(f"✅ użytkownik `{user}` (`{user.id}`) trafił na blacklistę.")

    @blacklist_cmd.sub_command(name="remove")
    async def bl_remove(self, ctx, user: discord.User):
        async with aiosqlite.connect("data/bot.db") as db:
            await db.execute("DELETE FROM blacklisted WHERE user_id=?", (user.id,))
            await db.commit()
        await ctx.respond(f"✅ usunięto `{user.id}` z blacklisty.")

    @blacklist_cmd.sub_command(name="list")
    async def bl_list(self, ctx):
        async with aiosqlite.connect("data/bot.db") as db:
            cur = await db.execute("SELECT user_id FROM blacklisted")
            rows = await cur.fetchall()
        if not rows:
            return await ctx.respond("❌ lista pusta.")
        ids = ", ".join(str(r[0]) for r in rows)
        await ctx.respond(f"Czarna lista: `{ids}`", ephemeral=True)


def setup(bot):
    bot.add_cog(BlacklistCog(bot))
