import asyncio
import discord
from discord.ext import commands


class Invite(commands.Cog):
	
	def __init__(self, client):
		self.client = client
		self.invites = dict()
		for g in self.client.guilds:
			asyncio.run_coroutine_threadsafe(self.update_invites(g), self.client.loop).result()
	
	def get_invitelog(self, guild):
		return self.client.dbconf_get(guild, 'invitelog')
	
	async def update_invites(self, guild):
		self.invites[guild.id] = await guild.invites()
	
	@commands.Cog.listener()
	async def on_guild_join(self, guild: discord.Guild):
		await self.update_invites(guild)
	
	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		guild = member.guild
		channelid = self.get_invitelog(guild.id)
		if channelid is None:
			return
		channel = self.client.get_channel(int(channelid))
		if channel is None:
			return
		new = await guild.invites()
		old = self.invites[guild.id]
		for index, invite in enumerate(old):
			if invite not in new:
				inviter = invite.inviter
				await channel.send(
					f"**{member}** ({member.id}) wurde von"
					f" **{inviter}** ({inviter.id}) eingeladen. (Onetime)")
				break
			else:
				if invite.uses != new[index].uses:
					inviter = invite.inviter
					await channel.send(
						f"**{member}** ({member.id}) wurde von **{inviter}** ({inviter.id}) eingeladen. "
						f"(Invite: {invite.code})")
					break
		else:
			await channel.send("Konnte Invite nicht tracken!")
		# If it throws an error a user managed to join a server that has no invite.
		await self.update_invites(guild)
	
	@commands.Cog.listener()
	async def on_invite_create(self, invite: discord.Invite):
		await self.update_invites(invite.guild)
	
	@commands.Cog.listener()
	async def on_invite_delete(self, invite: discord.Invite):
		await self.update_invites(invite.guild)


def setup(client):
	client.add_cog(Invite(client))
