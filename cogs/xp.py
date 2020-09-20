import discord
import random as r
import time as t
from discord.ext import commands

ADDITIONALXP = 20
BASEXP = 100
COOLDOWN_TIME = 30
voice_states = dict()


# Returns a Level to a certain xp amount
def level(x, rec_lev=0):
	return rec_lev if x - rec_lev * ADDITIONALXP <= BASEXP + ADDITIONALXP else level(
		x - rec_lev * ADDITIONALXP, rec_lev=rec_lev + 1)


# returns how much xp is needed for a level
def xp(input_level, k=0):
	return k + 100 + ADDITIONALXP if input_level == 0 else xp(input_level - 1, k=k + input_level * ADDITIONALXP)


def get_text_xp(length):
	if length < 10:
		return r.randint(0, 100) / 100
	else:
		return round((r.randint(100, 1000) + length) / (2100 - length), 2) * 5


def get_voice_xp(seconds):
	return round(seconds / 60 * r.randint(30, 70) / 20, 2)


class Xp(commands.Cog):
	
	def __init__(self, client):
		self.levels = [xp(lev) for lev in range(0, 250)]
		self.client = client
		self.cooldowns = dict()
	
	# TODO: "Garbage-Collector" der cooldowns cleart
	def finish_xp(self):
		print("Finish")
	
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
			await ctx.send(
				embed=discord.Embed(
					title="Dein Fortschritt" if userid == ctx.author.id else f"Fortschritt von User {disid}",
					description=
					f"**{lev}** {balken} **{lev + 1}**\nXP Fortschritt: **{round(percent * 100, 2)}%**"
					f" {round(xpx, 2)}/{xptick}"))
	
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
	
	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if member.guild.id not in voice_states.keys():
			voice_states[member.guild.id] = dict()
		
		def put_user_in():
			if member.id in voice_states[member.guild.id]:
				return
			voice_states[member.guild.id][member.id] = t.time()
		
		async def del_user():
			try:
				voice_time = t.time() - voice_states[member.guild.id][member.id]
				voice_states[member.guild.id].pop(member.id)
			except KeyError:
				return
			if voice_time < 30:
				return
			voice_xp = get_voice_xp(voice_time)
			with self.client.db.get(member.guild.id) as db:
				old = db.execute("SELECT xp FROM leveldata WHERE userId = ?", (member.id,)).fetchall()
				oldlev = 0
				if len(old) == 0:
					lev = 0
				else:
					voice_xp = float(old[0][0]) + voice_xp
					oldlev = self.get_level(old[0][0])
					lev = self.get_level(voice_xp)
				db.execute(
					"INSERT OR REPLACE INTO leveldata (userId, level, xp) VALUES (?, ?, ?)", (member.id, lev, voice_xp))
				
				if oldlev < lev:
					await self.client.send_dm(
						member, f":partying_face: LEVEL UP! Du bist nun Level {lev} <@{member.id}> :tada:")
		if after.channel is None or after.self_mute or after.self_deaf or after.afk:
			await del_user()
		else:
			put_user_in()


def setup(client):
	voice_states.clear()
	client.add_cog(Xp(client))


def teardown(client):
	print("TEARDOWN")
	# TODO TEARDOWN
	voice_states.clear()
