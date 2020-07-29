from discord.ext.commands import Bot as DBot


class CustomClient(DBot):

	def __init__(self, **options):
		super().__init__(**options)
		self.del_time_small = 20
		self.del_time_long = 60

	async def delete_cmd(self, ctx):
		if ctx.guild is None:
			return
		await ctx.channel.purge(limit=1)

	async def unverified(self):
		pass  # TODO

	async def verified(self):
		pass  # TODO

