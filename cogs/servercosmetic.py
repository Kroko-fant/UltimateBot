import json
import os
import re
import discord
from discord.ext import commands


class ServerCosmetic(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.reactionchannels = dict()
        for f in os.listdir("db"):
            if f.endswith(".db"):
                self.reactionchannels[int(f[0:-3])] = self.client.dbconf_get(int(f[0:-3]), "autoreact")
        with open("data/reactionchannels.json", "r") as f:
            self.reactionchannelemotes = json.load(f)

    @commands.command()
    async def addreact(self, ctx):
        """Erstellt eine neue reaction"""
        info_message = await ctx.send("Reagiere auf eine Nachricht um das Emote permanent zu adden")
        try:
            reaction, member = await self.client.rdecoder.wait_for_user_reaction(self.client, ctx.author, timeout=60)
        finally:
            await info_message.delete()
        await reaction.message.add_reaction(reaction.emoji)
        await reaction.remove(member)

    @commands.command()
    async def removereact(self, ctx):
        """Erstellt eine neue reaction"""
        info_message = await ctx.send("Reagiere auf eine Nachricht um das Emote permanent zu adden")
        try:
            reaction, member = await self.client.rdecoder.wait_for_user_reaction(self.client, ctx.author, timeout=60)
        finally:
            await info_message.delete()
        with self.client.db.get(ctx.guild.id) as db:
            if len(db.execute("SELECT * FROM reactionroles WHERE message == ? AND emoji == ?",
                              (reaction.message.id, str(reaction.emoji))).fetchall()) > 0:
                await ctx.send("Du kannst keine Reactionrole mit diesem Command entfernen!",
                               delete_after=self.client.del_time_small)
                return
        await reaction.message.remove_reaction(ctx.me, reaction.emoji)
        await reaction.remove(member)

    # Command to set Values in the Server Config
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set(self, ctx, key, value=""):
        """Setze eine Variable auf einen bestimmten Wert. Für Hilfe welche Variablen es gibt gebe !set help ein."""
        if key == "prefix":
            await ctx.send(f"Prefix wurde zu {value} geändert", delete_after=self.client.del_time_small)
        elif key == "vorgestellt":
            await ctx.send(f"{key.capitalize()}-Rolle erfolgreich gesetzt!", delete_after=self.client.del_time_small)
        elif key in ["bump", "logchannel", "botlog", "invitelog", "modlog", "vorstellen"]:
            if not self.client.get_channel(int(value)) in ctx.guild.channels:
                await ctx.send("Das ist kein gültiger Channel!")
                return
            await ctx.send(f"{key.capitalize()}-Channel erfolgreich gesetzt!", delete_after=self.client.del_time_small)
        elif key == "maxwarns":
            # A maximum of 10 warns per server should be enough
            if not value.isnumeric() or int(value) > 10 or int(value) < 1:
                await ctx.send(f"Das ist kein gültiger Integer! (Expected: Integer between 1 and 10 but was: {value}")
                return
            await ctx.send(f"{value} Warns sind nun die maximalen Warns!", delete_after=self.client.del_time_small)
        elif key == "warntime":
            # I assume that 7 days as a minimal ban time is fine.
            if not value.isnumeric() or int(value) < 7:
                await ctx.send(f"Das ist kein gültiger Integer! (Expected: Integer greater than 7 but was: {value}",
                               delete_after=self.client.del_time_small)
                return
            await ctx.send(f"Warn-Time wurde erfolgreich auf {value} Tage gesetzt.",
                           delete_after=self.client.del_time_small)
        elif key == "autoreact":
            if not self.client.get_channel(int(value)) in ctx.guild.channels:
                await ctx.send("Das ist kein gültiger Channel!", delete_after=self.client.del_time_small)
                return
            self.reactionchannels[ctx.guild.id] = value
            await ctx.send(f"Autoreactchannel wurde zu {value} geändert", delete_after=self.client.del_time_small)
        else:
            return await ctx.send(
                embed=discord.Embed(
                    title="Set-Help",
                    description=" Values:\n@prefix Der Botprefix des jeweiligen servers \n"
                                "@bump: discord.Channel.id Kanal, in welchem automatisch dlm!me gebumt werden soll.\n"
                                "@logchannel: discord.Channel.id Kanal in welchem der Log steht\n"
                                "@botlog: discord.Channel.id Kanal in welchem der Bot\n"
                                "@invitelog: discord.Channel.id Kanal in welchem\n"
                                "@modlog: discord.Channel.id Channel, in welchem der Moderationslog gesendet wird\n"
                                "@vorgestellt: discord.Role.id Rolle, welche ein Vorgestellter User bekommt\n"
                                "@maxwarns: int zeigt an wie viele Warns ein User maximal bekommen darf.\n"
                                "@warntime: int zeigt an wie viele Tage ein Warn erhalten bleibt."
                ))
        self.client.dbconf_set(ctx.guild.id, key, value)

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["rcaddemote"])
    async def reactionchanneladdemote(self, ctx, emote):
        def add_emote():
            if str(ctx.guild.id) not in self.reactionchannelemotes:
                self.reactionchannelemotes[str(ctx.guild.id)] = []
            if emote not in self.reactionchannelemotes[str(ctx.guild.id)]:
                self.reactionchannelemotes[str(ctx.guild.id)].append(emote)
                return True
            else:
                return False

        if emote.startswith("<") and emote.endswith(">"):
            emote = re.sub(r'[^\d]', "", emote)
            if self.client.get_emoji(int(emote)) is not None:
                await ctx.send("Ich kann das Emoji nicht verwenden!")
                return
        elif not emote.encode("unicode_escape").startswith(b"\U"):
            await ctx.send("Das ist kein Gültiges Emote!")
            return
        result = add_emote()
        if not result:
            await ctx.send("Emoji ist bereits vorhanden!")
            return
        with open("data/reactionchannels.json", "w") as f:
            json.dump(self.reactionchannelemotes, f, indent=4)

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["rcremoveemote"])
    async def reactionchannelremoveemote(self, ctx, emote):
        if emote.startswith("<") and emote.endswith(">"):
            emote = re.sub(r'[^\d]', "", emote)
        elif not emote.encode("unicode_escape").startswith(b"\U"):
            await ctx.send("Das ist kein Gültiges Emote!")
            return
        if str(ctx.guild.id) not in self.reactionchannelemotes:
            await ctx.send("Es gibt keine Emojis!")
            return
        if emote not in self.reactionchannelemotes[str(ctx.guild.id)]:
            await ctx.send("Es gibt das Emoji nicht!")
            return
        self.reactionchannelemotes[str(ctx.guild.id)].remove(emote)
        with open("data/reactionchannels.json", "w") as f:
            json.dump(self.reactionchannelemotes, f, indent=4)
        await ctx.send("Emoji wurde erfolgreich entfernt!")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check for invalid messages
        if message is None or message.guild is None:
            return
        if str(message.guild.id) in self.reactionchannelemotes and message.guild.id in self.reactionchannels and \
                str(message.channel.id) == self.reactionchannels[message.guild.id]:
            for x in self.reactionchannelemotes[str(message.guild.id)]:
                if x.encode("unicode_escape").startswith(b"\U"):
                    await message.add_reaction(emoji=x)
                else:
                    emoji = self.client.get_emoji(int(x))
                    if emoji is not None:
                        await message.add_reaction(emoji=emoji)


async def setup(client):
    await client.add_cog(ServerCosmetic(client))
