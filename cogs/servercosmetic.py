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


def setup(client):
	client.add_cog(ServerCosmetic(client))
