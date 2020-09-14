import discord
import re
import sqlite3
from discord.ext import commands


class Admin(commands.Cog):

	def __init__(self, client):
		self.client = client
		self.dmchannel = 635544300834258995

	@commands.command()
	@commands.is_owner()
	async def send(self, ctx, ch: discord.TextChannel, *, text):
		try:
			await ch.send(text)
		except discord.DiscordException:
			await ctx.message.add_reaction("⚠")
		else:
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
	
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.member.bot or message.guild is None:
			return
		# DMs empfangen
		if message.guild is None:
			channel = self.client.get_channel(int(self.dmchannel))
			content = f'**{message.author}** sagt: "{message.content}"'
			self.client.send(channel, content)
		# DMs senden
		elif message.channel.id == self.dmchannel and message.content[0:18].isnumeric():
			await message.add_reaction("✅")
			dmchannel = self.client.get_user(int(message.content[0:18]))
			if dmchannel.dm_channel is None:
				await dmchannel.create_dm()
			await dmchannel.dm_channel.send(message.content[19:])
	
	@commands.command()
	@commands.is_owner()
	async def sql(self, ctx, *, query):
		"""Executes a SQL-query"""
		matches = re.match(r'`(.*)`', query)
		if not matches:
			await ctx.send("Ungültige Eingabe der Query", delete_after=self.client.del_time_small)
			return

		query = matches.group(1)
		try:
			with self.client.db.get(ctx.guild.id) as db:
				result = [dict(row) for row in db.execute(query).fetchall()]
		except sqlite3.OperationalError as e:
			await ctx.send(f"```{e}```", delete_after=self.client.del_time_long)
			return
		if len(result) < 1:
			return
		keys = result[0].keys()
		key_length = {}
		for row in result:
			for key in keys:
				if key not in key_length:
					key_length[key] = len(str(key))

				key_length[key] = max(key_length[key], len(str(row[key])))
		text = "|"
		for i in keys:
			text += f" {str(i).ljust(key_length[i])} |"
		text += "\n" + '-' * len(text)
		for row in result:
			newtext = "\n|"
			for key in keys:
				newtext += f" {str(row[key]).ljust(key_length[key])} |"
			# -6: Account for code block
			if len(text) + len(newtext) >= 2000 - 6:
				await ctx.send(f"```{text}```", delete_after=self.client.del_time_long)
				text = ""
			text += newtext
		await ctx.send(f"```{text}```", delete_after=self.client.del_time_long)


def setup(client):
	client.add_cog(Admin(client))
