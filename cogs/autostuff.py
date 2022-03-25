from discord.ext import commands, tasks


class Autostuff(commands.Cog):
	
	def __init__(self, client):
		self.client = client
		self.bump.start()

	def cog_unload(self):
		self.bump.cancel()

	@tasks.loop(hours=9, minutes=30)
	async def bump(self):
		for g in self.client.guilds:
			chid = self.client.dbconf_get(g.id, "bump")
			if chid is None:
				continue
			channel = self.client.get_channel(int(chid))
			if channel is None:
				return
			await channel.send("dlm!bump")

	@bump.before_loop
	async def before_loop(self):
		await self.client.wait_until_ready()


async def setup(client):
	await client.add_cog(Autostuff(client))
