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
	# def finish_xp(self):
	# print("Finish")
	
	def get_level(self, userxp):
		if userxp < self.levels[0]:
			return 0
		for lev, x in enumerate(self.levels):
			if userxp < x:
				return lev - 1
	
	def get_vorstellen(self, guild_id):
		vorstellen = self.client.dbconf_get(guild_id, "vorstellen")
		if vorstellen is None:
			return None
		return vorstellen
	
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
					title=f"Fortschritt von User"
					f" {str(self.client.get_user(disid))[:-5] if userid != ctx.author.id else str(ctx.author)[:-5]}",
					description=f"**{lev}** {balken} **{lev + 1}**\nXP Fortschritt: **{round(percent * 100, 2)}%**"
					f" {round(xpx, 2)}/{xptick}"))
	
	@commands.command()
	async def top(self, ctx):
		def get_index(input_index):
			if input_index == 1:
				return ":first_place:"
			if input_index == 2:
				return ":second_place:"
			if input_index == 3:
				return ":third_place:"
			else:
				return f"**{input_index}**"
		
		with self.client.db.get(ctx.guild.id) as db:
			data = db.execute("SELECT * FROM leveldata ORDER BY xp DESC LIMIT 101").fetchall()
		
		description = "**Platz   User**"
		for index, row in enumerate(data, 1):
			description += f'\n{get_index(index)}  {str(self.client.get_user(row[0]))[:-5]}'
		
		await ctx.send(embed=discord.Embed(title=f"Rangliste von {ctx.guild}", description=description))

	@commands.Cog.listener()
	async def on_message(self, ctx):
		async def add_xp(bonusxp=0, force_dm=False):
			with self.client.db.get(ctx.guild.id) as db:
				old = db.execute("SELECT xp, level FROM leveldata WHERE userId = ?", (ctx.author.id,)).fetchall()
				oldlev = 0
				if len(old) == 0:
					x = round(get_text_xp(len(ctx.content)), 2) + bonusxp
				else:
					x = float(old[0][0]) + get_text_xp(len(ctx.content)) + bonusxp
					oldlev = old[0][1]
				
				lev = oldlev
				old_max_xp = self.levels[lev + 1]
				while x > old_max_xp:
					lev += 1
					x -= self.levels[oldlev]
					old_max_xp = self.levels[lev + 1]
				db.execute(
					"INSERT OR REPLACE INTO leveldata (userId, level, xp) VALUES (?, ?, ?)", (ctx.author.id, lev, x))
				if oldlev < lev:
					if force_dm:
						await self.client.send_dm(
							member=ctx.author,
							content=f":partying_face: LEVEL UP! Du bist nun Level {lev} <@{ctx.author.id}> :tada:")
					else:
						await ctx.channel.send(
							f":partying_face: LEVEL UP! Du bist nun Level {lev} <@{ctx.author.id}> :tada:")
		
		# Ignore DMs
		if ctx.guild is None or ctx.guild.id is None:
			return
		try:
			if t.time() - self.cooldowns[ctx.guild.id][ctx.author.id] < 60:
				return
		except KeyError:
			pass
		
		if str(ctx.channel.id) == self.get_vorstellen(ctx.guild.id):
			role_name = self.client.dbconf_get(ctx.guild.id, "vorgestellt")
			if role_name is None:
				pass
			else:
				
				role = ctx.guild.get_role(int(role_name))
				try:
					await ctx.author.add_roles(role, reason="Vorstellung")
				except Exception:
					pass
				else:
					await add_xp(bonusxp=100, force_dm=True)
					return
		
		# Cooldown
		if ctx.guild.id not in self.cooldowns.keys():
			self.cooldowns[ctx.guild.id] = dict()
		self.cooldowns[ctx.guild.id][ctx.author.id] = t.time()
		
		# Ignore Commands
		if ctx.content.startswith(self.client.get_server_prefix(ctx.guild.id)):
			return
		
		await add_xp()
	
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
			voice_xp =  round(get_voice_xp(voice_time), 2)
			with self.client.db.get(member.guild.id) as db:
				old = db.execute("SELECT xp, level FROM leveldata WHERE userId = ?", (member.id,)).fetchall()
				oldlev = 0
				if len(old) != 0:
					voice_xp =float(old[0][0]) + voice_xp
					oldlev = old[0][1]
				
				lev = oldlev
				old_max_xp = self.levels[lev + 1]
				while voice_xp > old_max_xp:
					lev += 1
					voice_xp -= self.levels[oldlev]
					old_max_xp = self.levels[lev + 1]
				
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
	# TODO TEARDOWN
	voice_states.clear()
