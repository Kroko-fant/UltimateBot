import json
import discord
from discord.ext import commands


class Anticheat(commands.Cog):

    def __init__(self, client):
        self.client = client
        with open('./data/blacklist.json', 'r') as f:
            self.blacklist = json.load(f)['0']

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        elif any([curse in message.content.lower() for curse in self.blacklist]):
            if message.content.startswith(f'{self.client.prefixes[message.guild.id]}blacklistadd'):
                return
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, das ist hier nicht erlaubt!", delete_after=self.client.del_time_small)

    @commands.command()
    @commands.is_owner()
    async def blacklistadd(self, ctx: commands.Context, curse):
        self.blacklist.append(curse.lower())
        with open('./data/blacklist.json', 'w') as f:
            json.dump({"0": self.blacklist}, f, indent=4)
        await ctx.send("Seite erfolgreich hinzugefügt!", delete_after=self.client.del_time_small)


def setup(client):
    client.add_cog(Anticheat(client))
