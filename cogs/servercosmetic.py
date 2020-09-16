import discord
from discord.ext import commands


class ServerCosmetic(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def set(self, ctx, key, value=""):
		"""Setze eine Variable auf einen bestimmten Wert. Für Hilfe welche Variablen es gibt gebe !set help ein."""
		
		async def setchannel(k):
			if not value.isnumeric():
				raise ValueError
			self.client.dbconf_set(ctx.guild.id, key, value)
			
		if key in ["prefix", "bump", "logchannel", "botlog", "invitelog"]:
			await setchannel(key)
			await ctx.send(f"{key.capitalize()}-Channel erfolgreich gesetzt!", delete_after=self.client.del_time_small)
		elif key == "prefix":
			self.client.dbconf_set(ctx.guild.id, key, value)
			await ctx.send(f"Prefix wurde zu {value} geändert", delete_after=self.client.del_time_small)
		else:
			await ctx.send(
				embed=discord.Embed(
					title="Set-Help",
					description=
					"bump\tSetzt den Kanal in welchem gebumpt werden soll\nlogchannel\tSetzt den Kanal in welchem der "
					"Log sein soll.\nbotlog\tSetzt den Kanal in welchem der Bot seine Statusmeldungen posten soll\n"
					"invitelog\tSetzt den Kanal in welchem der Bot Invites Trackt"))


def setup(client):
	client.add_cog(ServerCosmetic(client))
