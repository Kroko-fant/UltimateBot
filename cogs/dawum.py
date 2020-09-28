import json
import urllib
import matplotlib.pyplot as plt
import discord
import numpy as np
import asyncio
from discord.ext import commands


parlamentcodes = {
	'bt': 0, 'bundestag': 0, 'bw': 1, 'bawü': 1, 'de-bw': 1, 'baden': 1, 'badenwürttemberg': 1, 'by': 2,
	'bay': 2, 'de-by': 2, 'bayern': 2, 'be': 3, 'de-be': 3, 'berlin': 3, 'ber': 3, 'bb': 4, 'de-bb': 4,
	'brandenburg': 4, 'brand': 4, 'hb': 5, 'de-hb': 5, 'bremen': 5, 'hh': 6, 'de-hh': 6, 'hamburg': 6, 'ham': 6,
	'he': 7, 'de-he': 7, 'hessen': 7, 'mv': 8, 'de-mv': 8, 'mecklenburg': 8, 'vorpommern': 8,
	'mecklenburg-vorpommern': 8, 'ni': 9, 'de-ni': 9, 'nie': 9, 'nieder': 9, 'niedersachsen': 9, 'nw': 10,
	'de-nw': 10, 'nrw': 10, 'nordrhein': 10, 'westfalen': 10, 'nordrhein-westfalen': 10, 'rp': 11, 'de-rp': 11,
	'rheinland-pfalz': 11, 'rheinland': 11, 'pfalz': 11, 'sl': 12, 'de-sl': 12, 'saarland': 12, 'saar': 12,
	'sn': 13, 'de-sn': 13, 'sachsen': 13, 'sac': 13, 'st': 14, 'de-st': 14, 'sachsen-anhalt': 14,
	'anhalt': 14, 'sh': 15, 'de-sh': 15, 'schleswig-holstein': 15, 'schleswig': 15, "deutschland": 0,
	'holstein': 15, 'th': 16, 'de-th': 16, 'thüringen': 16, 'thü': 16, 'eu': 17, 'europa': 17, "de": 0}
partycodes = {
	'CDU': 101, 'CSU': 102, 'CDU/CSU': 1, 'SPD': 2, 'Die Grünen': 4, 'Afd': 7, 'Linke': 5, 'FDP': 3,
	'Freie-Wähler': 8, 'Brandenburger Vereinigte Bürgerbewegungen/Freie Wähler': 14, 'Piraten': 6,
	'Die Partei': 13, 'SSW': 10, 'Bayernpartei': 11, 'Tierschutz': 15, 'Bürger in Wut': 16, 'Sonstige': 0}
colors = {
	'CDU/CSU': '#000000', 'CDU': '#000000', 'CSU': '#0570C9', 'SPD': '#E3000F', 'Die Grünen': '#1AA037',
	'Linke': '#FF0000', 'FDP': '#FFEF00', 'Afd': '#0489DB', 'Die Partei': '#860028', 'Piraten': '#FE7400',
	'Sonstige': '#A9A9A9'}


def run_plotting(data, title):
	plt.rcdefaults()
	objects = tuple(data.keys())
	y_pos = np.arange(len(objects))
	colorlist = [colors[p] if p in colors else "#A9A9A9" for p in objects]
	performance = data.values()
	
	plt.bar(y_pos, performance, align='center', width=1, color=colorlist)
	plt.xticks(y_pos, objects)
	plt.ylabel('Stimmen in %')
	plt.title(title)
	plt.savefig("data/output.png")
	plt.clf()


def umfrage_ausgeben(parlacode, count):
	data = json.loads(urllib.request.urlopen("https://api.dawum.de/").read())
	if parlacode.isdigit():
		parlacode = int(parlacode)
		if not (-1 < parlacode):
			return None
		
		umfragenid = [parlacode] if int(parlacode) > 18 \
			else [int(k) for k, v in data['Surveys'].items() if v['Parliament_ID'] == str(parlacode)]
	else:
		if parlacode not in parlamentcodes:
			return None
		parlacode = str(parlamentcodes[parlacode])
		umfragenid = [int(k) for k, v in data['Surveys'].items() if v['Parliament_ID'] == str(parlacode.lower())]
	
	if len(umfragenid) < count:
		count = len(umfragenid)
	newids = []
	for ids in range(count):
		newids.append(max(umfragenid))
		umfragenid.remove(max(umfragenid))
	
	if count == 1:
		output = f"von **{data['Institutes'][data['Surveys'][str(newids[0])]['Institute_ID']]['Name']}" \
			f"** am {data['Surveys'][str(newids[0])]['Date']}\n"
	else:
		output = f"Die aktuellsten {count} Umfragen.\n"
	
	party_scores = dict()
	
	for party in partycodes.keys():
		score = 0.0
		for elements in newids:
			try:
				score += int(data['Surveys'][str(elements)]['Results'][str(partycodes[party])])
			except KeyError:
				pass
		if score > 0:
			score = round(score / count, 2)
			party_scores[party] = score
			output += f"\n** {party}**: {score} %"

	run_plotting(data=party_scores, title=data['Parliaments'][data['Surveys'][str(newids[0])]['Parliament_ID']]['Name'])

	wahlembed = discord.Embed(
		title=data['Parliaments'][data['Surveys'][str(newids[0])]['Parliament_ID']]['Name'],
		description=output, color=12370112)
	wahlembed.set_footer(
		text=f"UmfragenId: {newids[0]}\n Daten aus der Dawum APi: https://dawum.de/"
		if count == 1 else "Daten aus der Dawum APi: https://dawum.de/")

	return wahlembed


class Dawum(commands.Cog):
	
	def __init__(self, client):
		self.client = client
		self.lock = asyncio.Lock()
	
	@commands.command(aliases=["umfrage"])
	async def poll(self, ctx, parla="bt", count=1):
		"""Gebe die aktuelle Wahlumfrage aus.
		Syntax: !poll <ländercode> <Umfragenzahl>
		Der Ländercode ist optional. Alle Ländercodes sind intuitiv. Umfragenzahl"""
		async with self.lock:
			if parla.lower() == "help":
				wahlhelfembed = discord.Embed(
					description="Verwendung: !poll oder !poll <ländercode> <range>. Länderkürzel der deutschen Bundesländer,"
					" Bundestag oder EU Range beliebig wählbar (<= 10) und es wird ein gemittelter Durchschnitt berechnet",
					title="Hilfe zum Befehl !poll", color=12370112)
				await ctx.send(embed=wahlhelfembed, delete_after=self.client.del_time_mid)
			else:
				if count < 1:
					await ctx.send(embed=discord.Embed(
						title="Error!", description="Count muss >= 1 sein"))
					return
				result = umfrage_ausgeben(parla, int(count))
				if result is None:
					await ctx.send(embed=discord.Embed(
						title="Error!", description="Dein Parlament konnte nicht gefunden werden!"))
				else:
					await ctx.send(embed=result)
					await ctx.send(file=discord.File("data/output.png"))


def setup(client):
	client.add_cog(Dawum(client))
