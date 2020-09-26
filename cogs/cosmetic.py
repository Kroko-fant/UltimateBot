import time

import discord
from discord.ext import commands


# A class containing cosmetic stuff and some basic about stuff
class Cosmetic(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_command(self, ctx):
		await ctx.message.delete(delay=60)

	@commands.command()
	async def version(self, ctx):
		"""Zeigt die aktuelle Bot-Version."""
		await ctx.send(
			f'Der Bot läuft auf :eyes~1: **Version Release 1.2.0**. Die API läuft auf Version :mailbox: '
			f'**{discord.__version__}**', delete_after=self.client.del_time_mid)
	
	@commands.command()
	async def about(self, ctx):
		"""Zeigt Informationen über den Bot an."""
		embed = discord.Embed(description='Bot programmiert von Krokofant#0909.', title='Über den Bot!')
		embed.set_footer(text=f'UltimateBot 2019-{time.struct_time(time.gmtime())[0]}')
		await ctx.send(embed=embed, delete_after=self.client.del_time_mid)


def setup(client):
	client.add_cog(Cosmetic(client))
