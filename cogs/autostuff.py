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
			try:
				if chid is None:
					return
				channel = self.client.get_channel(int(chid))
				if channel is None:
					return
			except Exception:
				continue
			await channel.send("dlm!bump")

	@bump.before_loop
	async def before_loop(self):
		await self.client.wait_until_ready()


def setup(client):
	client.add_cog(Autostuff(client))
