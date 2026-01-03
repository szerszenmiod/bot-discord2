import discord

def has_support_role(member, role_id):
    return discord.utils.get(member.roles, id=role_id)
