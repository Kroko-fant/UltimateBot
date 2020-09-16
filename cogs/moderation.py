import re as r
import discord
from discord.ext import commands


class Moderation(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def clear(self, ctx, amount=10):
		"""Löscht den gewählten Amount an Nachrichten Standardmenge: 10"""
		await ctx.send(f"Es wurden **{amount}** Nachrichten gelöscht.", delete_after=self.client.del_time_mid)

	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, *, reason="Kick-Befehl wurde benutzt"):
		"""Kickt den User vom Server Syntax: {prefix}kick <@user>"""
		await member.kick(reason=reason)
		await ctx.send(f"User **{member}** wurde gekickt.", delete_after=self.client.del_time_mid)

	@commands.command()
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		"""Ban den User vom Server Syntax: {prefix}ban <@user>"""
		await member.ban(reason=reason)
		await ctx.send(f"User **{member}** wurde gebannt.", delete_after=self.client.del_time_mid)
	
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def multiban(self, ctx, *, member_input):
		members = r.split(r"\D+", member_input)
		members = list(dict.fromkeys(members))
		members.remove("")
		for m in members:
			await ctx.guild.get_member(int(m)).ban(reason="Multiban")


def setup(client):
	client.add_cog(Moderation(client))
