from discord.ext import commands


# A class containing cosmeticas for the bot in Form of events.
class Cosmetic(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_command(self, ctx):
		await ctx.message.delete(delay=15)


def setup(client):
	client.add_cog(Cosmetic(client))
