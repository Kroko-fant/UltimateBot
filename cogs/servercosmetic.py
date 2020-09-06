import discord
from discord.ext import commands


class ServerCosmetic(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def prefix(self, ctx, prefix):
		# TODO: Permissionlevel
		self.client.prefixes[ctx.guild.id] = prefix
		self.client.dbconf_set(ctx.guild.id, "prefix", prefix)
		await ctx.send(f"Prefix wurde zu {prefix} geändert", delete_after=self.client.del_time_small)
	
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def set(self, ctx, key, value=""):
		"""Setze eine Variable auf einen bestimmten Wert. Für Hilfe welche Variablen es gibt gebe !set help ein."""
		
		def setchannel(k):
			if not value.isnumeric():
				await ctx.send("Das ist kein gültiger Discord-Kanal!")
			self.client.dbconf_set(ctx.guild.id, key, value)
			await ctx.send(f"{k.capitalize()}-Channel erfolgreich gesetzt!")
		
		if key in ["bump", "log", "botlog", "invitelog"]:
			setchannel(key)
		else:
			await ctx.send(
				embed=discord.Embed(
					title="Set-Help",
					description=
					"bump\tSetzt den Kanal in welchem gebumpt werden soll\nlog\tSetzt den Kanal in welchem der Log sein"
					" soll.\nbotlog\tSetzt den Kanal in welchem der Bot seine Statusmeldungen posten soll\n"
					"invitelog\tSetzt den Kanal in welchem der Bot Invites Trackt"))


def setup(client):
	client.add_cog(ServerCosmetic(client))
