import json
import discord
from discord.ext import commands


class Autoverify(commands.Cog):

	def __init__(self, client):
		self.client = client
		with open('./data/roles/mainrole.json', 'r') as m:
			self.mainroles = json.load(m)
		with open('./data/roles/spacer.json', 'r') as s:
			self.spacers = json.load(s)
	
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def mainrole(self, ctx, role: discord.Role):
		"""Setze die Rolle die neue User bekommen"""
		if role.guild is ctx.guild:
			self.mainroles[str(ctx.guild.id)] = int(role.id)
			with open('./data/roles/mainrole.json', 'w') as f:
				json.dump(self.mainroles, f, indent=4)
			await ctx.send("Main-Rolle gesetzt.", delete_after=self.client.del_time_mid)
		else:
			await ctx.send("Rolle wurde auf dem Server nicht gefunden.", delete_after=self.client.del_time_mid)
	
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def spacer(self, ctx, mode, role: discord.Role):
		"""Füge eine Spacerrolle hinzu oder entferne diese"""
		if role.guild.id != ctx.guild.id and (mode == "add" or mode == "remove"):
			print(role.guild)
			print(ctx.guild)
			await ctx.send("Rolle wurde auf dem Server nicht gefunden.", delete_after=self.client.del_time_mid)
		elif mode == "add":
			if str(ctx.guild.id) not in self.spacers.keys():
				self.spacers[str(ctx.guild.id)] = []
			self.spacers[str(ctx.guild.id)].append(role.id)
			with open('./data/roles/spacer.json', 'w') as f:
				json.dump(self.spacers, f, indent=4)
			await ctx.send(f'Rolle {role} hinzugefügt.', delete_after=self.client.del_time_mid)
		elif mode == "remove":
			self.spacers[str(ctx.guild.id)].remove(role.id)
			with open('./data/roles/spacer.json', 'w') as f:
				json.dump(self.spacers, f, indent=4)
			await ctx.send("Spacerrolle entfernt.", delete_after=self.client.del_time_mid)
		else:
			await ctx.send("Ungültiger Mode! Verfügbare Modi:\nadd\tremove")
		
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.guild is not None and message.author is not None and isinstance(message.author, discord.Member) \
				and len(message.author.roles) == 1:
			try:
				member = message.guild.get_member(int(message.author.id))
				# Main Rolle setzen
				role = message.guild.get_role(self.mainroles[str(message.guild.id)])
				await member.add_roles(role, reason="verify (mainrole)")
				# Spacer setzen
				for rid in self.spacers[str(message.guild.id)]:
					trole = message.guild.get_role(rid)
					await member.add_roles(trole, reason="verify (spacer)")
			except KeyError:
				pass


def setup(client):
	client.add_cog(Autoverify(client))
