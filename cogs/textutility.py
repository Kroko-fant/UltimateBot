import discord
import datetime as dt
from discord.ext import commands, tasks


# 60 sekunden 60 minuten 24 stunden 3 tage
ARCHIV_TIME = 60 * 60 * 24 * 3


class TextUtility(commands.Cog):
	
	def __init__(self, client):
		self.client = client
		self.topiccreate = dict()
		self.categorys = dict()
		self.archives = dict()
	
	def cog_unload(self):
		self.themen_garbage_collector.cancel()
	
	def init_modul(self):
		for g in self.client.guilds:
			try:
				self.topiccreate[g.id] = int(self.client.dbconf_get(g.id, "create"))
				self.categorys[g.id] = int(self.client.dbconf_get(g.id, "category"))
				self.archives[g.id] = int(self.client.dbconf_get(g.id, "archiv"))
			except TypeError:
				pass
			except IndexError:
				pass
		self.themen_garbage_collector.start()
	
	@tasks.loop(hours=1)
	async def themen_garbage_collector(self):
		now = dt.datetime.utcnow()
		
		def initalise(guild_id):
			local = self.client.get_guild(guild_id)
			return local, local.get_channel(self.archives[guild_id]), local.get_channel(self.categorys[guild_id])
		
		async def clean_archive(archive):
			if len(archive.voice_channels) > 0:
				for voice_channel in archive.voice_channels:
					await voice_channel.delete()
			elif len(archive.channels) >= 50:
				del_channel, time = 0, now
				for ch in archive.text_channels:
					msg = await ch.history(limit=1).next()
					if time > msg.created_at:
						del_channel, time = ch, msg.created_at
				await del_channel.delete()
		
		for guildid in self.archives.keys():
			try:
				guild, archivcategory, category = initalise(guildid)
			except Exception:
				continue
			
			for channel in category.text_channels:
				if guildid in self.topiccreate and channel.id == self.topiccreate[guildid]:
					continue
				try:
					message = await channel.history(limit=1).next()
				except discord.errors.NoMoreItems:
					await channel.delete()
				else:
					if round((now - message.created_at).total_seconds()) > ARCHIV_TIME:
						await clean_archive(archive=archivcategory)
						await channel.edit(reason="Archivieren", category=archivcategory)
	
	@commands.Cog.listener()
	async def on_ready(self):
		self.init_modul()

	@commands.command()
	@commands.is_owner()
	async def fixthemen(self, ctx):
		self.init_modul()
		await ctx.send("Themen gefixt!")

	# Command to set Values in the Server Config
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def textchannel(self, ctx, key, value=""):
		"""Setzt einen textchannel <key>, <value> nutze den Key help für eine übsericht aller Keys"""
		async def setchannel():
			if not value.isnumeric():
				raise ValueError
			self.client.dbconf_set(ctx.guild.id, key, value)

		if key == "create":
			await setchannel()
			await ctx.send(f"{key.capitalize()}-Channel erfolgreich gesetzt!", delete_after=self.client.del_time_small)
			self.topiccreate[ctx.guild.id] = int(self.client.dbconf_get(ctx.guild.id, "create"))
		elif key == "category":
			await setchannel()
			await ctx.send(f"{key.capitalize()}-Channel erfolgreich gesetzt!", delete_after=self.client.del_time_small)
			self.categorys[ctx.guild.id] = int(self.client.dbconf_get(ctx.guild.id, "category"))
		elif key == "archiv":
			await setchannel()
			await ctx.send(f"{key.capitalize()}-Channel erfolgreich gesetzt!", delete_after=self.client.del_time_small)
			self.archives[ctx.guild.id] = int(self.client.dbconf_get(ctx.guild.id, "archiv"))
		else:
			await ctx.send(
				embed=discord.Embed(
					title="Textchannel-Help",
					description="create\tKanal zum erstellen von Kanälen\ncategory\tSetzt die Kategorie in welcher "
					"Kanäle erstellt werden sollen\nauto-react\tSetzt einen Kanal für automatische Reaktionen"))
	
	# wenn message im Topic Channel
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.guild is None or message.author.id == self.client.user.id or \
				message.guild.id not in self.topiccreate.keys() or \
				message.guild.id not in self.archives.keys():
			return
		elif message.channel.category_id == self.archives[message.guild.id]:
			category = message.guild.get_channel(self.categorys[message.guild.id])
			if len(category.channels) < 20:
				await message.channel.edit(category=category)
		elif message.channel.id == self.topiccreate[message.guild.id]:
			await message.delete()
			if message.author.bot:
				await message.channel.send(
					"Nachrichten anderer Bots sind hier nichte erlaubt bitte führe hier keine Befehle aus!",
					delete_after=self.client.del_time_mid)
			elif len(str(message.content)) > 100:
				await message.channel.send(
					"Zu Langer Titel! Dein Titel beim Thema erstellen ist zu lang! (>100 Zeichen)",
					delete_after=self.client.del_time_mid)
			else:
				
				try:
					# neuer channel erstellen
					category = message.guild.get_channel(self.categorys[message.guild.id])
					if category is None:
						raise KeyError
					new = await category.create_text_channel(
						message.content, position=0, topic=message.content,
						reason=f"Neuer Channel von User {str(message.author)} zum Thema {message.content}")
					await message.channel.send(
						f"Channel {message.content} erfolgreich erstellt.", delete_after=self.client.del_time_small)
					await new.send(embed=discord.Embed(
						title=f"Neues Thema {message.content}",
						description=f"Das neue Thema {message.content} wurde von User <@{message.author.id}> erstellt."))
				except KeyError:  # Konnte Kategorie nicht finden
					await message.channel.send(
						f"Konnte keine Kategorie für ein neues Thema finden. Bitte kontaktiere einen Admin und "
						f"bitte ihn eine Kategorie mit {self.client.prefixes[message.guild.id]}textchannel kategorie "
						f"zu setzen. Oder diesen Kanal als Themen-Erstellungskanal zu entfernen.",
						delete_after=self.client.del_time_long)
				except discord.DiscordException:
					await message.send(
						"Konnte den Kanal nicht erstellen. Bitte überprüfe deinen Kanalnamen.",
						delete_after=self.client.del_time_mid)


def setup(client):
	client.add_cog(TextUtility(client))
