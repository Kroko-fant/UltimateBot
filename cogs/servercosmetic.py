import discord
from discord.ext import commands


class ServerCosmetic(commands.Cog):

	def __init__(self, client):
		self.client = client
	
	# Command to set Values in the Server Config
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def set(self, ctx, key, value=""):
		"""Setze eine Variable auf einen bestimmten Wert. Für Hilfe welche Variablen es gibt gebe !set help ein."""
		
		async def set_key_value():
			if not value.isnumeric():
				raise ValueError
			self.client.dbconf_set(ctx.guild.id, key, value)
			
		if key in ["bump", "logchannel", "botlog", "invitelog", "vorstellen"]:
			await set_key_value()
			await ctx.send(f"{key.capitalize()}-Channel erfolgreich gesetzt!", delete_after=self.client.del_time_small)
		elif key == "vorgestellt":
			await set_key_value()
			await ctx.send(f"{key.capitalize()}-Rolle erfolgreich gesetzt!", delete_after=self.client.del_time_small)
		elif key == "prefix":
			await set_key_value()
			await ctx.send(f"Prefix wurde zu {value} geändert", delete_after=self.client.del_time_small)
		else:
			await ctx.send(
				embed=discord.Embed(
					title="Set-Help",
					description="bump\tSetzt den Kanal in welchem gebumpt werden soll\nlogchannel\tSetzt den Kanal in "
					"welchem der Log sein soll.\nbotlog\tSetzt den Kanal in welchem der Bot seine Statusmeldungen "
					"posten soll\ninvitelog\tSetzt den Kanal in welchem der Bot Invites Trackt\nvorstellen\tSetzt"
					"den Kanal in welchem sich User vorstellen können.\nvorgestellt\tSetzt die vorgestellt Rolle"))


def setup(client):
	client.add_cog(ServerCosmetic(client))
