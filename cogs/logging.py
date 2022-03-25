from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_logchannel(self, guild):
        return self.client.dbconf_get(guild, 'logchannel')

    async def log_stuff(self, member, message):
        if not member.bot:
            if (log_channel_id := self.get_logchannel(member.guild.id)) is None:
                return
            if (log_channel := self.client.get_channel(int(log_channel_id))) is None:
                return
            await log_channel.send(message)

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

        if (log_channel_id := self.get_logchannel(payload.guild_id)) is None:
            return
        log_channel = self.client.get_channel(int(log_channel_id))

        if payload.cached_message is None:
            await self.client.send(
                log_channel, f":recycle: Nachricht in {payload.message_id} gelöscht. Content nicht mehr im Cache.")
            return
        content = payload.cached_message.clean_content
        member = payload.cached_message.author
        channel = payload.cached_message.channel
        await self.client.send(
            log_channel, f":recycle: Nachricht ({payload.message_id}) von **{member}** ({member.id}) in Channel "
                         f"#**{channel}** ({payload.channel_id}) gelöscht mit dem Inhalt:\n{content}")

    # Voice-Änderungen
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member is None or member.guild is None:
            return
        if (log_channel_id := self.get_logchannel(member.guild.id)) is None:
            return
        if (log_channel := self.client.get_channel(int(log_channel_id))) is None:
            return
        if before.channel is None:
            await log_channel.send(
                f":mega: **{member} ({member.id})** hat den Voice Channel **{after.channel}** betreten.")
        elif before.channel is not None and after.channel is None:
            await log_channel.send(
                f":mega: **{member} ({member.id})** hat den Voice Channel **{before.channel}** verlassen.")
        elif before.channel != after.channel:
            await log_channel.send(
                f":mega: **{member} ({member.id} )** hat den Voice Channel von ** {before.channel} ** zu ** "
                f"{after.channel}** gewechselt.")
        else:
            if before.self_deaf != after.self_deaf:
                if before.self_deaf:
                    await log_channel.send(f':microphone2: **{member} ({member.id})** hat seine Kopfhöhrer entmutet')
                else:
                    await log_channel.send(f':microphone2: **{member} ({member.id})** hat seine Kopfhöhrer gemutet')
            if before.self_mute != after.self_mute:
                if before.self_mute:
                    await log_channel.send(f':microphone2: **{member} ({member.id})** hat sein Mikrofon entmutet')
                else:
                    await log_channel.send(f':microphone2: **{member} ({member.id})** hat sein Mikrofon gemutet')


async def setup(client):
    await client.add_cog(Logging(client))
