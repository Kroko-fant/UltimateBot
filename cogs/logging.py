from discord.ext import commands


class Logging(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	def get_logchannel(self, guild):
		return self.client.dbconf_get(guild, 'logchannel')
	
	async def log_stuff(self, member, message):
		try:
			if member.client:
				logchannelid = self.get_logchannel(member.guild.id)
				if logchannelid is None:
					return
				logch = self.client.get_channel(int(logchannelid))
				await logch.send(message)
		except Exception:
			pass
	
	# Memberleave
	@commands.Cog.listener()
	async def on_member_join(self, member):
		await self.log_stuff(member, f":inbox_tray: **{member}** ({member.id}) hat den Server betreten.")
		
	# Memberleave
	@commands.Cog.listener()
	async def on_member_remove(self, member):
		await self.log_stuff(member, f":outbox_tray: **{member}** ({member.id}) hat den Server verlassen.")
	
	# Member wird gebannt
	@commands.Cog.listener()
	async def on_member_ban(self, _, member):
		await self.log_stuff(member, f":no_entry_sign: **{member}** ({member.id}) wurde gebannt.")
	
	# Member wird entbannt
	@commands.Cog.listener()
	async def on_member_unban(self, _, member):
		await self.log_stuff(member, f":white_check_mark: **{member}** ({member.id}) wurde entgebannt.")
	
	# Nachricht löschen
	@commands.Cog.listener()
	async def on_raw_message_delete(self, payload):
		if payload.guild_id is None:
			return
		logchannelid = self.get_logchannel(payload.guild_id)
		if logchannelid is None:
			return
		logch = self.client.get_channel(int(logchannelid))
		try:
			ch = payload.channel_id
			msg = payload.message_id
			content = payload.cached_message.clean_content
			member = payload.cached_message.author
			channel = payload.cached_message.channel
			string = \
				f":rcycle: Nachricht ({msg.id}) von **{member}** ({member.id}) in Channel **{channel}** ({ch}) " \
				f"gelöscht mit dem Inhalt:\n{content}"
			self.client.send(logch, string)
		except Exception:
			pass

	# Voice-Änderungen
	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if member is None or member.guild is None:
			return
		logch = self.get_logchannel(member.guild.id)
		if logch is None:
			return
		logch = self.client.get_channel(int(logch))
		if before.channel is None:
			await logch.send(
				f":mega: **{member} ({member.id})** hat den Voice Channel **{after.channel}** betreten.")
		elif before.channel is not None and after.channel is None:
			await logch.send(
				f":mega: **{member} ({member.id})** hat den Voice Channel **{before.channel}** verlassen.")
		elif before.channel != after.channel:
			await logch.send(
				f":mega: **{member} ({member.id} )** hat den Voice Channel von ** {before.channel} ** zu ** "
				f"{after.channel}** gewechselt.")
		else:
			if before.self_deaf != after.self_deaf:
				if before.self_deaf:
					await logch.send(f':microphone2: **{member} ({member.id})** hat seine Kopfhöhrer entmutet')
				else:
					await logch.send(f':microphone2: **{member} ({member.id})** hat seine Kopfhöhrer gemutet')
			if before.self_mute != after.self_mute:
				if before.self_mute:
					await logch.send(f':microphone2: **{member} ({member.id})** hat sein Mikrofon entmutet')
				else:
					await logch.send(f':microphone2: **{member} ({member.id})** hat sein Mikrofon gemutet')


def setup(client):
	client.add_cog(Logging(client))
