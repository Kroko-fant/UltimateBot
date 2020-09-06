import discord
import random as r
from discord.ext import commands


ADDITIONALXP = 20
BASEXP = 100


# Returns a Level to a certain xp amount
def level(x, l=0):
	return l if x - l * ADDITIONALXP <= BASEXP + ADDITIONALXP else level(x - l * ADDITIONALXP, l=l + 1)


# returns how much xp is needed for a level
def xp(l, k=0):
	return k + 100 + ADDITIONALXP if l == 0 else xp(l - 1, k=k + l * ADDITIONALXP)


def get_text_xp(length):
	if length < 10:
		return 0.1
	else:
		return r.randint(0, 1000) / (2020 - length)


class Xp(commands.Cog):
	
	def __init__(self, client):
		self.levels = [xp(lev) for lev in range(0, 250)]
		self.client = client
	
	def get_level(self, userxp):
		if userxp < self.levels[0]:
			return 0
		for lev, x in enumerate(self.levels):
			if userxp < x:
				return lev - 1
	
	@commands.command()
	async def xp(self, ctx, userid=None):
		if userid is None:
			userid = ctx.author.id
			
		def parseXP(disid):
			with self.client.db.get(ctx.guild.id) as db:
				row = db.execute("SELECT xp, level FROM leveldata WHERE userId = ?", (disid,)).fetchall()
				return disid, row[0][1], row[0][0], self.levels[row[0][1] + 1]
		try:
			disid, lev, xpx, xptickm = parseXP(userid)
		except BaseException:
			await ctx.send("UserID konnte nicht gefunden werden!")
		else:
			if disid == ctx.author.id:
				await ctx.send(embed=discord.Embed(
					title=f'Deine aktuellen Stats:',
					description=f'Level: **{lev}**\nXP: **{xpx}**\nNächstes Level ab XP: **{xptickm}**'))
			else:
				await ctx.send(embed=discord.Embed(
					title=f'Daten von User: {self.client.get_user(disid)}',
					description=f'Level: **{lev}**\nXP: **{xpx}**\nNächstes Level ab XP: **{xptickm}**'))
		finally:
			pass
		
	@commands.Cog.listener()
	async def on_message(self, ctx):
		# Ignore DMs
		if ctx.guild.id is None:
			return
		
		# TODO: Cooldown
		# Ignore Commands
		if ctx.content.startswith(self.client.prefixes[ctx.guild.id]):
			return
		
		with self.client.db.get(ctx.guild.id) as db:
			old = db.execute("SELECT xp FROM leveldata WHERE userId = ?", (ctx.author.id,)).fetchall()
			oldlev = 0
			if len(old) == 0:
				x = round(get_text_xp(len(ctx.content)), 2)
				lev = 0
			else:
				x = round(float(old[0][0]) + get_text_xp(len(ctx.content)), 2)
				oldlev = self.get_level(old[0][0])
				lev = self.get_level(x)
			db.execute("INSERT OR REPLACE INTO leveldata (userId, level, xp) VALUES (?, ?, ?)", (ctx.author.id, lev, x))
			if oldlev < lev:
				await ctx.channel.send(f"LEVEL UP! Du bist nun Level {lev} <@{ctx.author.id}")

	@commands.Cog.listener()
	async def on_member_join(self, member):
		with self.client.db.get(member.guild.id) as db:
			db.execute("INSERT OR REPLACE INTO leveldata (userId, level, xp) VALUES (?, ?, ?)", (member.id, 0, 0))

	@commands.Cog.listener()
	async def on_member_leave(self, member):
		with self.client.db.get(member.guild.id) as db:
			db.execute("DELETE FROM leveldata WHERE userId LIKE ?", (member.id,))


def setup(client):
	client.add_cog(Xp(client))
