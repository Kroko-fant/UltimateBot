import logging
import os
import discord
import customclient
import time as t

from discord.ext import commands

import SECRETS
from dbmgr import DbMgr


def get_prefix(client, message):
	if message.guild is None:
		return '!'
	else:
		return client.dbconf_get(message.guild.id, 'prefix', '!')


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
	filename=f'[{t.struct_time(t.gmtime())[0]}-{t.struct_time(t.gmtime())[1]}-{t.struct_time(t.gmtime())[2]}]-['
	f'{t.struct_time(t.gmtime())[3]}_{t.struct_time(t.gmtime())[4]}]-discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
client = customclient.CustomClient(command_prefix=get_prefix, db=DbMgr("db"))


def load_modules():
	# Module beim Botstart laden
	for filename in os.listdir('./cogs'):
		if filename.endswith(".py"):
			if not filename.startswith('test'):
				client.load_extension(f'cogs.{filename[:-3]}')
				print(filename[:-3] + ' aktiviert')
		elif filename.endswith('__pycache__'):
			print('Py-Cache gefunden')
		else:
			print('\x1b[6;30;42m' + f"Fehlerhafte File auf dem Server gefunden! {filename}" + '\x1b[0m')
	print('Module geladen')


async def reload_modules(ctx):
	for filename in os.listdir('./cogs'):
		if filename.endswith(".py") and not filename.startswith('test'):
			try:
				client.reload_extension(f'cogs.{filename[:-3]}')
				await ctx.send(f':white_circle: {filename[:-3]} neugeladen.', delete_after=client.del_time_long)
			except commands.ExtensionError:
				await ctx.send(
					f':red_circle: {filename[:-3]} konnte nicht neugeladen werden.', delete_after=client.del_time_long)
		elif filename.endswith('__pycache__'):
			await ctx.send(f':blue_circle: Pycache vorhanden', delete_after=client.del_time_long)
		else:
			await ctx.send(f"Fehlerhafte File auf dem Server gefunden! {filename}", delete_after=client.del_time_long)


@client.event
async def on_ready():
	await client.change_presence(status=discord.Status.online, activity=discord.Game('Bot online und bereit'))
	print('Status geändert\nModule werden geladen')
	load_modules()


@client.command()
async def ping(ctx):
	"""Zeigt den aktuellen Ping"""
	await ctx.send(
		f'Pong! Meine Latenz sind aktuell {round(client.latency * 1000)} ms.', delete_after=client.del_time_long)


@client.command()
@commands.is_owner()
async def status(ctx, *, status_text):
	await client.change_presence(status=discord.Status.online, activity=discord.Game(status_text))
	await ctx.send(f'Der Status lautet nun: **{status_text}**', delete_after=client.del_time_long)


@client.command()
@commands.is_owner()
async def load(ctx, extension):
	"""Lädt ein Modul in den Bot"""
	client.load_extension(f'cogs.{extension.lower()}')
	await ctx.send(f":green_circle: {extension} aktiviert", delete_after=client.del_time_long)
	print(f'{extension} aktiviert')


@client.command()
@commands.is_owner()
async def unload(ctx, extension):
	"""Lädt ein Modul aus dem Bot"""
	client.unload_extension(f'cogs.{extension.lower()}')
	print(f'{extension} deaktiviert')
	await ctx.send(f':red_circle: {extension} deaktiviert', delete_after=client.del_time_long)


@client.command()
@commands.is_owner()
async def reload(ctx, extension):
	"""Lädt ein Modul neu"""
	if extension == "all":
		await reload_modules(ctx)
	else:
		client.reload_extension(f'cogs.{extension.lower()}')
		await ctx.send(f':white_circle: {extension} neugeladen.', delete_after=client.del_time_long)


@client.command()
@commands.is_owner()
async def shutdown(ctx):
	"""Fährt den Bot herunter.
	Danach muss man ihn auf dem Server in der Console neustarten lol."""
	await client.delete_cmd(ctx)
	await ctx.send("Bot wird heruntergefahren...")
	await client.logout()


# Errorhandler for Extension-Errors
@client.event
async def on_command_error(ctx, error, force=False):
	if hasattr(ctx.command, 'on_error') and not force:
		return
	error = getattr(error, 'original', error)
	if not isinstance(error, commands.ExtensionError):
		return
	
	# Extension already loaded
	if isinstance(error, commands.ExtensionAlreadyLoaded):
		await ctx.send(f"Die Extension ist bereits geladen!")
	# Extension not loaded
	elif isinstance(error, commands.ExtensionNotLoaded):
		await ctx.send(f"Die Extension ist nicht geladen!")
	elif isinstance(error, commands.NoEntryPointError):
		await ctx.send(f"Die Extension hat keinen EntryPoint (missing Setup)!")
	# Extension wirft Fehler
	elif isinstance(error, commands.ExtensionFailed):
		await ctx.send(f"Die Extension ist bereits geladen!")
	# Extension not found
	elif isinstance(error, commands.ExtensionNotFound):
		await ctx.send(f"Die Erweiterung konnte nicht gefunden werden.")
	# Extension konnte nicht regestriert werden
	elif isinstance(error, commands.CommandRegistrationError):
		await ctx.send(f"Der Command konnte nicht registriert werden, da er bereits vorhanden ist.")
	# Sonstige Extensionfehler
	elif isinstance(error, commands.ExtensionError):
		await ctx.send("Eine Erweiterung hat einen Fehler verursacht.")


print("Botstart abgeschlossen!")

client.run(SECRETS.TOKEN)
print(f'{client.user} ist jetzt online')
number = 0
for s in range(len(client.guilds)):
	number += 1
print(f'Bot läuft auf {number} Servern')
