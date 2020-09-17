import discord
import random as r
import time as t
from discord.ext import commands

ADDITIONALXP = 20
BASEXP = 100
COOLDOWN_TIME = 60


# Returns a Level to a certain xp amount
def level(x, rec_lev=0):
	return rec_lev if x - rec_lev * ADDITIONALXP <= BASEXP + ADDITIONALXP else level(
		x - rec_lev * ADDITIONALXP, rec_lev=rec_lev + 1)


# returns how much xp is needed for a level
def xp(input_level, k=0):
	return k + 100 + ADDITIONALXP if input_level == 0 else xp(input_level - 1, k=k + input_level * ADDITIONALXP)


def get_text_xp(length):
	if length < 10:
		return r.randint(0, 100) / 50
	else:
		return round((r.randint(100, 1000) + length) / (2222 - length), 2)


class Xp(commands.Cog):
	
	def __init__(self, client):
		self.levels = [xp(lev) for lev in range(0, 250)]
		self.client = client
		self.cooldowns = dict()
	
	# TODO: "Garbage-Collector" der cooldowns cleart
	
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
		
		def parseXP(dis_id):
			with self.client.db.get(ctx.guild.id) as db:
				row = db.execute("SELECT xp, level FROM leveldata WHERE userId = ?", (dis_id,)).fetchall()
				return dis_id, row[0][1], row[0][0], self.levels[row[0][1] + 1]
		
		try:
			disid, lev, xpx, xptick = parseXP(userid)
		except BaseException:
			await ctx.send("UserID konnte nicht gefunden werden!")
		else:
			balken = ""
			percent = round(xpx / xptick, 4)
			for i in range(0, 10):
				if i / 10 < percent < (i + 1) / 10:
					balken += ":blue_square:"
				elif i / 10 < percent:
					balken += ":green_square:"
				else:
					balken += ":red_square:"
			
			description = f"**{lev}** {balken} **{lev + 1}**\nXP Fortschritt: **{percent * 100}%** {xpx}/{xptick}"
			if userid == ctx.author.id:
				title = "Dein Fortschritt"
			else:
				title = f"Fortschritt von User {disid}"
			await ctx.send(
				embed=discord.Embed(
					title=title,
					description=description))
		finally:
			pass
	
	@commands.Cog.listener()
	async def on_message(self, ctx):
		# Ignore DMs
		if ctx.guild is None or ctx.guild.id is None:
			return
		try:
			if t.time() - self.cooldowns[ctx.guild.id][ctx.author.id] < 60:
				return
		except KeyError:
			pass
		
		# Cooldown
		if ctx.guild.id not in self.cooldowns.keys():
			self.cooldowns[ctx.guild.id] = dict()
		self.cooldowns[ctx.guild.id][ctx.author.id] = t.time()
		
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
				x = float(old[0][0]) + get_text_xp(len(ctx.content))
				oldlev = self.get_level(old[0][0])
				lev = self.get_level(x)
			db.execute("INSERT OR REPLACE INTO leveldata (userId, level, xp) VALUES (?, ?, ?)", (ctx.author.id, lev, x))
			if oldlev < lev:
				await ctx.channel.send(f":partying_face: LEVEL UP! Du bist nun Level {lev} <@{ctx.author.id}> :tada:")
	
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
