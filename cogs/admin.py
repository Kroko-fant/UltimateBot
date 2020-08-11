import discord
from discord.ext import commands


class Admin(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.is_owner()
	async def send(self, ctx, ch: discord.TextChannel, *, text):
		try:
			await ch.send(text)
		except discord.DiscordException:
			await ctx.message.add_reaction("⚠")
			return
		await ctx.message.add_reaction(self.client.get_emoji(634870836255391754))

	@commands.command(aliases=["dm", "pm"])
	@commands.is_owner()
	async def senddm(self, ctx, user: discord.User, *, text):
		if user.dm_channel is None:
			await user.create_dm()
		try:
			await user.dm_channel.send(text)
		except discord.DiscordException:
			await ctx.message.add_reaction("⚠")
			return
		await ctx.message.add_reaction(self.client.get_emoji(634870836255391754))


def setup(client):
	client.add_cog(Admin(client))
