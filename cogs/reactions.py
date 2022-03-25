import asyncio
import functools
from discord.ext import commands
import discord


def decode_reaction(func):
    @functools.wraps(func)
    async def wrapper(self, payload: discord.RawReactionActionEvent):
        reaction, member = await self.client.rdecoder.decode_raw_reaction(self.client, payload)
        return await func(self, reaction, member)

    return wrapper


class ReactionRoles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(aliases=["rr"], invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def reactionroles(self, ctx):
        """Managed reactionroles"""
        await ctx.send_help(ctx.command)
        return

    @reactionroles.command(aliases=["append"])
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, role: discord.Role):
        """Erstellt eine neue reactionrole"""

        if ctx.author.top_role <= role and ctx.author != ctx.guild.owner:
            await ctx.send("Diese Rolle ist höher als deine aktuelle!", delete_after=60)
            return

        if ctx.guild.me.top_role <= role:
            await ctx.send("Diese Rolle ist höher als meine aktuelle!", delete_after=60)
            return
        info_message = await ctx.send("Reagiere auf eine Nachricht mit einem Emoji um den Setup abzuschließen")

        try:
            reaction, member = await self.client.rdecoder.wait_for_user_reaction(self.client, ctx.author, timeout=60)
        finally:
            await info_message.delete()

        message = reaction.message
        guild = message.guild

        with self.client.db.get(guild.id) as db:
            result = db.execute("SELECT * FROM reactionroles WHERE message == ? AND emoji == ? AND role = ?",
                             (message.id, str(reaction.emoji), role.id)).fetchall()
            if len(result) > 0:
                await ctx.send("Hey du hast das Emoji bereits dieser Rolle zugewiesen!")
                return
            db.execute("INSERT INTO reactionroles(message, emoji, role) VALUES(?, ?, ?)",
                       (message.id, str(reaction.emoji), role.id))

        await message.add_reaction(reaction.emoji)
        await reaction.remove(member)

    @reactionroles.command(aliases=["remove"])
    @commands.has_permissions(manage_roles=True)
    async def delete(self, ctx):
        """Löscht eine reactionrole"""

        info_message = await ctx.send("Reagiere auf eine Nachricht um die Reaktion zu entfernen")

        try:
            reaction, member = await self.client.rdecoder.wait_for_user_reaction(self.client, ctx.author, timeout=60)
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
    async def on_reaction_add(self, reaction, member):
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
            if (role:= discord.utils.get(guild.roles, id=int(entry[0]))) in member.roles:
                await member.remove_roles(role)
            else:
                await member.add_roles(role)

        await reaction.remove(member)

    @add.error
    @delete.error
    async def handle_error(self, ctx, error):
        original = getattr(error, 'original', error)

        if isinstance(original, asyncio.TimeoutError):
            await ctx.send("Zu langsam! sei das nächste Mal etwas schneller")
            return
        if isinstance(original, discord.Forbidden):
            return

        # Defer to common error handler
        errhandler = self.client.get_cog('ErrorHandler')

        if errhandler is not None:
            await errhandler.on_command_error(ctx, error, force=True)


async def setup(client):
    await client.add_cog(ReactionRoles(client))
