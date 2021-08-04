import asyncio
import functools

from discord.ext import commands
import discord


async def _decode_raw_reaction(client, payload: discord.RawReactionActionEvent):
    # Fetch all the information
    guild = client.get_guild(payload.guild_id)
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = guild.get_member(payload.user_id)

    # Construct reaction
    reaction = discord.Reaction(message=message, data={'me': member == guild.me}, emoji=payload.emoji)

    return reaction, member


def decode_reaction(func):
    @functools.wraps(func)
    async def wrapper(self, payload: discord.RawReactionActionEvent):
        reaction, member = await _decode_raw_reaction(self.client, payload)
        return await func(self, reaction, member)

    return wrapper


async def _wait_for_user_reaction(client, user, timeout=60):
    payload = await client.wait_for('raw_reaction_add', check=lambda p: p.user_id == user.id, timeout=timeout)
    return await _decode_raw_reaction(client, payload)


class ReactionRoles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(aliases=["rr"], invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def reactionroles(self, ctx: commands.Context):
        """Managed Reactionroles"""
        await ctx.send_help(ctx.command)
        return

    @reactionroles.command(aliases=["append"])
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx: commands.Context, role: discord.Role):
        """Erstellt eine Reactionrole"""

        if ctx.author.top_role <= role and ctx.author != ctx.guild.owner:
            await ctx.send("Diese Rolle ist höher oder deiner aktuellen Rolle entsprechend", delete_after=60)
            return

        if ctx.guild.me.top_role <= role:
            await ctx.send("Deine Zielrolle ist höher als meine aktuelle Rolle", delete_after=60)
            return

        info_message = await ctx.send("Reagiere auf eine Nachricht um den Setup abzuschließen")

        try:
            reaction, member = await _wait_for_user_reaction(self.client, ctx.author, timeout=60)
        finally:
            await info_message.delete()

        message = reaction.message
        guild = message.guild

        with self.client.db.get(guild.id) as db:
            result = db.execute("SELECT * FROM reactionroles WHERE message == ? AND emoji == ? AND role = ?",
                             (message.id, str(reaction.emoji), role.id)).fetchall()
            if len(result) > 0:
                await ctx.send("Hey dieses Emoji ist bereits auf dieser Rolle!")
                return
            db.execute("INSERT INTO reactionroles(message, emoji, role) VALUES(?, ?, ?)",
                       (message.id, str(reaction.emoji), role.id))

        await message.add_reaction(reaction.emoji)
        await reaction.remove(member)

    @reactionroles.command(aliases=["remove"])
    @commands.has_permissions(manage_roles=True)
    async def delete(self, ctx:commands.Context):
        """Löscht eine Reacrtionrole"""

        info_message = await ctx.send("Reaiere mit einem Emoji auf eine Nachricht um ein Emoji zu entfernen!")

        try:
            reaction, member = await _wait_for_user_reaction(self.client, ctx.author, timeout=60)
        finally:
            await info_message.delete()

        message = reaction.message
        guild = message.guild

        with self.client.db.get(guild.id) as db:
            db.execute("DELETE FROM reactionroles WHERE message = ? AND emoji = ?", (message.id, str(reaction.emoji)))

        await reaction.remove(guild.me)
        await reaction.remove(member)

    @commands.Cog.listener(name="on_raw_reaction_add")
    @decode_reaction
    async def on_reaction_add(self, reaction: discord.Reaction, member):
        if reaction.me:
            return

        message = reaction.message
        guild = message.guild

        with self.client.db.get(guild.id) as db:
            result = db.execute("SELECT DISTINCT role FROM reactionroles WHERE message = ? AND emoji = ?",
                                (message.id, str(reaction.emoji))).fetchall()

        if len(result) == 0:
            return

        for entry in result:
            role = discord.utils.get(guild.roles, id=int(entry[0]))
            if role in member.roles:
                await member.remove_roles(role)
            else:
                await member.add_roles(role)

        await reaction.remove(member)

    # TODO: Implement a list command

    @add.error
    @delete.error
    async def handle_error(self, ctx: commands.Context, error: commands.CommandError):
        original = getattr(error, 'original', error)

        if isinstance(original, asyncio.TimeoutError):
            await ctx.send("Operation timed out. Füge die Reaktion schneller hinzu!")
            return
        if isinstance(original, discord.Forbidden):
            await ctx.send("Ich habe kein Rechte dies zu tun!")
            return

        # Defer to common error handler
        errhandler = self.client.get_cog('ErrorHandler')

        if errhandler is not None:
            await errhandler.on_command_error(ctx, error, force=True)


def setup(client):
    client.add_cog(ReactionRoles(client))
