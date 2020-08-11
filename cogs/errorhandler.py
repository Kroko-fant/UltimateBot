import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):

	def __init__(self, client):
		self.client = client

	# ErrorHandler
	@commands.Cog.listener()
	async def on_command_error(self, ctx, error, force=False):
		await ctx.message.delete(delay=10)
		# Skippen, wenn wir einen lokalen Handler haben
		if hasattr(ctx.command, 'on_error') and not force:
			return
		error = getattr(error, 'original', error)
		# Bypass
		if isinstance(error, commands.ExtensionError):
			return
		# Missing Permissions
		if isinstance(error, (commands.errors.MissingPermissions, commands.errors.NotOwner)):
			await ctx.send("Dazu fehlen dir die Permissions :P")
		# Fehlendes erwartetes Argument
		elif isinstance(error, commands.errors.MissingRequiredArgument):
			await ctx.send("Fehlendes Argument! gucke dir doch !help <command> an")
		elif isinstance(error, commands.errors.CommandNotFound):
			if ctx.message.content[1:].startswith("bump") or ctx.message.content[1:].isnumeric() or \
					ctx.message.content[1:].startswith("d bump") or ctx.message.content[1:].startswith("disboard"):
				return
			await ctx.send("Diesen Befehl gibt es nicht :(")

		# Sonstige Errors
		elif isinstance(error, discord.errors.Forbidden):
			await ctx.send(f"403-Forbidden Mir sind Hände und Füße gebunden ich habe keine Rechte!")
		elif isinstance(error, discord.InvalidData):
			await ctx.send(f'InvalidData - Discord hat mir komische Daten gesendet...')
		elif isinstance(error, (discord.InvalidArgument, commands.BadArgument, commands.BadUnionArgument)):
			await ctx.send(f'Dieses Argument ist nicht erlaubt für diese Methode.')
		# DiscordErrors
		elif isinstance(error, commands.CommandError):
			await ctx.send(f"Irgendwas funktioniert da nicht ganz...{error} {type(error)} <@!137291894953607168>")
		# Sonstige Errors
		else:
			await ctx.send(f"Ein unerwarteter Fehler ist aufgetreten! \n{error} {type(error)} <@!137291894953607168>")


def setup(client):
	client.add_cog(ErrorHandler(client))
