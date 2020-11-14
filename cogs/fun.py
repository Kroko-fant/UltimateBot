import random

import discord
from discord.ext import commands


class Fun(commands.Cog):
	
	def __init__(self, client):
		self.client = client
	
	@commands.command()
	async def metafrage(self, ctx):
		"""Gibt den Meta-Fragen-Text wider"""
		metafrageembed = discord.Embed(
			title="Metafrage",
			description='Du hast gerade eine Metafrage gestellt. Eine Metafrage ist eine unnötige Frage über der '
			'HauptFrage. Dies ist zwar höflich, aber ziemlich umständlich, da man seine Frage dann zwei mal stellen '
			'muss. \n\nDie Frage "Kennt sich jemand mit x aus?" hilft leider auch nicht weiter. Die Anwesenden könnten'
			' eventuell bei dem Problem helfen, obwohl sie nicht von sich behaupten würden, mit dem Thema vertraut zu '
			'sein. Und auch wenn jemand mit dem erfragten Thema vertraut ist, bedeutet dies nicht, dass er/sie eine'
			' spezielle Frage zu diesem Thema beantworten kann – niemand ist allwissend.\n\nDeswegen, stelle bitte '
			'einfach deine Frage anstatt "Darf ich etwas fragen" oder "kennt sich jemand mit x und y aus?" zu schreiben.'
			' Selbst, wenn es eine komplizierte oder sehr spezielle Frage ist, die du mehrere Minuten lang formulieren'
			' müsstest, dann mach das bitte. Wir wissen sonst nicht, ob wir sie beantworten könnten. \n'
			'Weitere Infos findest du unter http://metafrage.de/')
		metafrageembed.set_footer(text="Quelle: http://metafrage.de/")
		metafrageembed.set_thumbnail(url="https://cdn.pixabay.com/photo/2015/10/31/12/00/question-1015308_960_720.jpg")
		await ctx.send(embed=metafrageembed)
	
	@commands.command(aliases=["flip"])
	async def coinflip(self, ctx):
		"""Werfe eine Münze und erhalte kopf oder Zahl."""
		flip = random.randint(0, 1)
		if flip == 1:
			await ctx.send("Du hast **Kopf** geworfen!")
		elif flip == 0:
			await ctx.send("Du hast **Zahl** geworfen!")
		else:
			await ctx.send("Irgendwie hat das nicht ganz geklappt...", delete_after=self.client.del_time_mid)
	
	@commands.command()
	async def randomnumber(self, ctx, int2=100):
		"""Gebe eine zufällige Zahl zwischen 0 und x ein.
		Syntax: {prefix}randomnumber <x>
		Hat x keinen Wert bekommt x automatisch 100 zugewiesen."""
		if int2 <= 0:
			await ctx.send("Deine Zahl sollte größer als 0 sein!")
		else:
			await self.client.send(ctx, f"Deine Nummer zwischen 0 und {int2} lautet: **{random.randint(0, int2)}**")
	
	@commands.command()
	async def card(self, ctx):
		"""Lasse einen Pinguin eine Karte ziehen"""
		karten = [
			":diamonds: 7", ":diamonds: 8", ":diamonds: 9", ":diamonds: 10", ":diamonds: Bube", ":diamonds: Dame",
			":diamonds: Koenig", ":diamonds: Ass", ":hearts: 7", ":hearts: 8", ":hearts: 9", ":hearts: 10",
			":hearts: Bube", ":hearts: Dame", ":hearts: Koenig", ":hearts: Ass", ":spades: 7", ":spades: 8",
			":spades: 9", ":spades: 10", ":spades: Bube", ":spades: Dame", ":spades: Koenig", ":spades: Ass",
			":clubs: 7", ":clubs: 8", ":clubs: 9", ":clubs: 10", ":clubs: Bube", ":clubs: Dame", ":clubs: Koenig",
			":clubs: Ass"]
		await ctx.send(f"Du hast folgende Karte gezogen: **{karten[random.randint(0, 31)]}**")

	@commands.command()
	async def userinfo(self, ctx, member: discord.Member = None):
		"""Zeigt Informationen über einen Pinguin an."""
		if member is None:
			member = ctx.author
		roles = [role for role in member.roles]

		userinfoembed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

		userinfoembed.set_author(name=f'🐧 Informationen über: {member}')
		userinfoembed.set_thumbnail(url=member.avatar_url)
		userinfoembed.set_footer(text=f'{member} abgefragt von {ctx.author}', icon_url=ctx.author.avatar_url)

		userinfoembed.add_field(name='ID:', value=str(member.id))
		userinfoembed.add_field(name='Name:', value=str(member.display_name))
		userinfoembed.add_field(name='Status:', value=str(member.status))
		if member.activity is not None:
			userinfoembed.add_field(name='Aktivität:', value=str(member.activity.name))
		userinfoembed.add_field(
			name='Account erstellt:', value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
		userinfoembed.add_field(name='Beigetreten:', value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
		userinfoembed.add_field(name=f'Rollen ({len(roles)})', value='  '.join([role.mention for role in roles]))
		userinfoembed.add_field(name='Höchste Rolle:', value=str(member.top_role.mention))
		userinfoembed.add_field(name='Bot?', value=str(member.bot))
		
		await ctx.send(embed=userinfoembed)


def setup(client):
	client.add_cog(Fun(client))
