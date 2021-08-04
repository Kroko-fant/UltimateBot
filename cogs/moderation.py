import asyncio
import re as r
from datetime import datetime

import discord
from discord.ext import commands


# TODO: Perm-Level
class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.warn_lock = asyncio.Lock()

    # TODO Task to revoke warnings
    # TODO Autounban

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount=10):
        """Löscht den gewählten Amount an Nachrichten Standardmenge: 10"""
        await ctx.channel.purge(limit=int(amount))
        await ctx.send(f"Es wurden **{amount}** Nachrichten gelöscht.", delete_after=self.client.del_time_mid)

    async def add_warn(self, guild, member: discord.Member, reason):
        banned = False
        # Fetch max warns
        with self.client.db.get(guild.id) as db:
            # Insert the warn even if the bot crashes after that task the warn will be inserted.
            # This part is highly prioritized
            db.execute(
                "INSERT INTO warns (userid, reason, timestamp) VALUES (?, ?, ?)",
                (member.id, reason, str(datetime.now())))
            # Check other warns of the user
            rows = db.execute("SELECT * FROM warns WHERE userid = ?", (member.id,)).fetchall()
        max_warns = self.client.dbconf_get(guild.id, "maxwarns")
        if max_warns is not None and len(rows) >= int(max_warns):
            # TODO implement unban date
            # Dein Unban erfolgt am {}
            # Send the user a DM
            banned = True
            await guild.ban(member, reason="Du hast zu viele Warns erhalten.")
        # Send a message in the Mod-log
        mod_log = self.client.dbconf_get(guild.id, "modlog")

        if mod_log is None:
            return
        channel = guild.get_channel(int(mod_log))
        if channel is None:
            return

        await channel.send(
            embed=discord.Embed(
                title=f"Ban für User {member}" if banned else f"Warn für User {member}",
                description=reason,
                colour=discord.Colour.red() if banned else discord.Colour.orange()
            )
        )

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason="Kein Grund angegeben"):
        """Warnt einen Nutzer. Es kann festgelegt werden wann Warns verfallen."""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("Du kannst keine User verwarnen, die höher oder gleichgestellt sind.")
            return

        await self.add_warn(ctx.guild, member, reason)
        await ctx.message.add_reaction(self.client.get_emoji(634870836255391754))

    @commands.command()
    async def warns(self, ctx: commands.Context, member: discord.Member = None):
        """Zeigt eigene beziehungsweise die Warns eines Users an"""
        if member is None:
            member = ctx.author
        # Fetch Warns
        with self.client.db.get(ctx.guild.id) as db:
            warns = db.execute("SELECT * FROM warns WHERE userid = ?", (member.id,)).fetchall()
        content = ""
        if len(warns) == 0:
            content = f"{member} hat bisher keine Warns."
        else:
            for i, r in enumerate(warns, 1):
                # Todo: Implement time when the warn will be rewoked
                content += f"# {i} für {r[1]} am {r[2]}\n"

        if not await self.client.send_dm(ctx.author, discord.Embed(
                title=f"Warns von User {member}",
                description=content), embed=True):
            await ctx.send("Ich kann dir leider keine DMs senden!", delete_after=self.client.del_time_mid)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason="Kick-Befehl wurde benutzt"):
        """Kickt den User vom Server Syntax: {prefix}kick <@user>"""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("Du kannst keine Leute kicken die einen gleich hohen/höheren Rang haben")
        elif ctx.guild.me <= member.top_role:
            await ctx.send("Ich kann keine Leute kicken die einen gleich hohen/höheren Rang haben")
        else:
            await member.kick(reason=reason)
            await ctx.send(f"User **{member}** wurde gekickt.", delete_after=self.client.del_time_mid)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason=None):
        """Ban den User vom Server Syntax: {prefix}ban <@user>"""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("Du kannst keine Leute bannen die einen gleich hohen/höheren Rang haben")
        elif ctx.guild.me.top_role <= member.top_role:
            await ctx.send("Ich kann keine Leute bannen die einen gleich hohen/höheren Rang haben")
        else:
            await member.ban(reason=reason)
            await ctx.send(f"User **{member}** wurde gebannt.", delete_after=self.client.del_time_mid)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def multiban(self, ctx: commands.Context, *, member_input):
        members = r.split(r"\D+", member_input)
        members = list(dict.fromkeys(members))
        members.remove("")
        for m in members:
            member = ctx.guild.get_member(int(m))
            if ctx.author.top_role <= member.top_role:
                continue
            await member.ban(reason="Multiban")


def setup(client):
    client.add_cog(Moderation(client))
