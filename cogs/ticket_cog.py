import discord, aiosqlite
from discord.ext import commands
from utils.embeds import ticket_embed
from utils.transcript import save_transcript

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="panel")
    @commands.has_permissions(manage_channels=True)
    async def panel(self, ctx):
        from config_json import cats
        options = [
            discord.SelectOption(label=v["label"], emoji=v.get("emoji"), value=k)
            for k, v in cats.items()
        ]
        sel = discord.ui.Select(
            custom_id="ticket_create", placeholder="🎫 Wybierz kategorię ticketu...", options=options
        )
        view = discord.ui.View().add_item(sel)
        await ctx.respond(
            embed=ticket_embed("System Ticketów", "Kliknij i wybierz kategorię."), view=view
        )

    @discord.ui.select(custom_id="ticket_create")
    async def create_ticket(self, interaction: discord.Interaction, select):
        cat_key = select.values[0]
        cat = cats[cat_key]

        guild, user = interaction.guild, interaction.user
        # Sprawdź blacklist
        async with aiosqlite.connect("data/bot.db") as db:
            rows = await db.execute("SELECT 1 FROM blacklisted WHERE user_id=?", (user.id,))
            if await rows.fetchone():
                return await interaction.response.send_message(
                    "❌ Jesteś zablokowany!", ephemeral=True
                )

        # Tworzenie kanału
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        sup_role = guild.get_role(cat["role"])
        if sup_role:
            overwrites[sup_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.display_name}",
            category=guild.get_channel(cat["cat"]),
            overwrites=overwrites,
            topic=f"Ticket utworzony przez {user} ({user.id})"
        )
        await db.execute(
            """INSERT INTO tickets(guild_id,user_id,channel_id,category)
               VALUES(?,?,?,?)""",
            (guild.id, user.id, channel.id, cat_key),
        )
        await db.commit()

        questions = "\n".join([f"**{q}:** [odpowiedź]" for q in cat["questions"]])
        welcome = ticket_embed(
            f"{cat['emoji']}  {cat['label']} – Ticket #{channel.name.split('-')[-1]}",
            f"Pytania:\n{questions}",
            cat.get("color", 0x3498db),
        )
        await channel.send(content=f"{user.mention}", embed=welcome)

        await interaction.response.send_message(
            f"✅ Stworzono kanał {channel.mention}", ephemeral=True
        )


def setup(bot):
    bot.add_cog(TicketCog(bot))
