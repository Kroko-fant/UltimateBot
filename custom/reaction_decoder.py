import discord


class ReactionDecoder:

    async def decode_raw_reaction(self, client, payload: discord.RawReactionActionEvent):
        # Fetch all the information
        guild = client.get_guild(payload.guild_id)
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = guild.get_member(payload.user_id)

        # Construct reaction
        reaction = discord.Reaction(message=message, data={'me': member == guild.me}, emoji=payload.emoji)

        return reaction, member

    async def wait_for_user_reaction(self, client, user, timeout=60):
        payload = await client.wait_for('raw_reaction_add', check=lambda p: p.user_id == user.id, timeout=timeout)
        return await self.decode_raw_reaction(client, payload)
