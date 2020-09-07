from discord.ext import commands
import discord


# TODO: DO Permlevels
class ReactionRoles(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.active = {}
	
	@commands.group(invoke_without_command=True)
	@commands.has_permissions(manage_roles=True)
	async def rr(self, ctx):
		"""Verwaltet Reactionroles"""
		pass
	
	@rr.command()
	@commands.has_permissions(manage_roles=True)
	async def add(self, ctx, role: discord.Role):
		"""Erstellt eine neue Reaction Role"""
		if ctx.author.top_role <= role:
			await ctx.send(
				"Du kannst keine Rolle einer Reaktion zuweisen die höher als deine aktuelle Rolle ist.", delete_after=60)
			return
		self.active[ctx.author.id] = role.id
		await ctx.send("Reagiere auf eine Nachricht um den Setup abzuschließen", delete_after=self.client.del_time_long)

	@rr.command()
	@commands.has_permissions(manage_roles=True)
	async def remove(self, ctx):
		"""Löscht eine Reaction Role"""
		self.active[ctx.author.id] = None
		await ctx.send(
			"Reagiere auf eine Nachricht mit einem Emoji um dieses zu löschen", delete_after=self.client.del_time_long)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		guild = self.client.get_guild(payload.guild_id)
		channel = self.client.get_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		member = guild.get_member(payload.user_id)
		
		if member == guild.me:
			return
		
		if member.id in self.active:
			if self.active[member.id] is None:
				with self.client.db.get(guild.id) as db:
					db.execute(
						"DELETE FROM reactionroles WHERE message = ? AND emoji = ?",
						(message.id, str(payload.emoji)))
				await message.remove_reaction(payload.emoji, guild.me)
			else:
				with self.client.db.get(guild.id) as db:
					db.execute(
						"INSERT INTO reactionroles(message, emoji, role) VALUES(?, ?, ?)",
						(message.id, str(payload.emoji), self.active[member.id]))
				await message.add_reaction(payload.emoji)
			await message.remove_reaction(payload.emoji, member)
			self.active.pop(member.id)
			return
		with self.client.db.get(guild.id) as db:
			result = db.execute(
				"SELECT role FROM reactionroles WHERE message = ? AND emoji = ?",
				(message.id, str(payload.emoji))).fetchall()
		if len(result) == 0:
			return
		for entry in result:
			role = discord.utils.get(guild.roles, id=int(entry[0]))
			await member.add_roles(role)
		await message.remove_reaction(payload.emoji, member)


def setup(client):
	client.add_cog(ReactionRoles(client))
