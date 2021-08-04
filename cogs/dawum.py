import json
import urllib.request as request
import matplotlib.pyplot as plt
import discord
import numpy as np
import asyncio
from discord.ext import commands

# Notice! You are not allowed to use this module without giving the credits to https://dawum.de/api/

parlamentcodes = {
    'bt': 0, 'bundestag': 0, 'bw': 1, 'bawü': 1, 'de-bw': 1, 'baden': 1, 'baden-württemberg': 1, 'by': 2,
    'bay': 2, 'de-by': 2, 'bayern': 2, 'be': 3, 'de-be': 3, 'berlin': 3, 'ber': 3, 'bb': 4, 'de-bb': 4,
    'brandenburg': 4, 'brand': 4, 'hb': 5, 'de-hb': 5, 'bremen': 5, 'hh': 6, 'de-hh': 6, 'hamburg': 6, 'ham': 6,
    'he': 7, 'de-he': 7, 'hessen': 7, 'mv': 8, 'de-mv': 8, 'mecklenburg': 8, 'vorpommern': 8,
    'mecklenburg-vorpommern': 8, 'ni': 9, 'de-ni': 9, 'nie': 9, 'nieder': 9, 'niedersachsen': 9, 'nw': 10,
    'de-nw': 10, 'nrw': 10, "nordrhein-westfalen (nrw)": 10, 'nordrhein': 10, 'westfalen': 10,
    'nordrhein-westfalen': 10, 'rp': 11, 'de-rp': 11, "europäisches parlament": 17,
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


# creates a plot! and saves it in data/output.png That has to be synchronized
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


# Creates an embed with an poll
def umfrage_ausgeben(parlacode, count: int):
    data = json.loads(request.urlopen("https://api.dawum.de/").read())
    # Check own shortcuts
    if not parlacode.isdigit():
        if parlacode not in parlamentcodes:
            return None
        parlacode = str(parlamentcodes[parlacode])
        umfragen_ids = [int(k) for k, v in data['Surveys'].items() if v['Parliament_ID'] == str(parlacode.lower())]
    # If its not a valid parlament maybe it is a survey ID.
    elif not (parlacode in data['Parliaments']):
        # If its a valid ID umfragen_ids is the one.
        if parlacode in data['Surveys']:
            umfragen_ids = [parlacode]
        else:
            return None
    else:
        umfragen_ids = [int(k) for k, v in data['Surveys'].items() if v['Parliament_ID'] == parlacode]

    parlament_name = data['Parliaments'][data['Surveys'][str(umfragen_ids[0])]['Parliament_ID']]['Name']

    # Count must be the minimum of the list of all available IDs and tha requested count
    count = min(len(umfragen_ids), count)
    for _ in range(len(umfragen_ids) - count):
        umfragen_ids.remove(min(umfragen_ids))

    # Determinate which subtitle to choose
    if count == 1:
        output = f"von **{data['Institutes'][data['Surveys'][str(umfragen_ids[0])]['Institute_ID']]['Name']}** " \
                 f"am {data['Surveys'][str(umfragen_ids[0])]['Date']}\n"
    else:
        output = f"Die aktuellsten {count} Umfragen.\n"

    party_scores = dict()

    # Count results for partys
    for party in partycodes.keys():
        score = 0.0
        for element in umfragen_ids:
            # Ignores Errors. Providing a chart has priority
            try:
                score += int(data['Surveys'][str(element)]['Results'][str(partycodes[party])])
            except KeyError:
                continue
        if score > 0:
            score = round(score / count, 2)
            party_scores[party] = score
            output += f"\n** {party}**: {score} %"

    # Runs the plotting and gives an output.png
    run_plotting(data=party_scores, title=parlament_name)

    # creates the embed
    wahlembed = discord.Embed(title=parlament_name, description=output, color=12370112)
    wahlembed.set_footer(text=
                         (f"umfragen_ids: {umfragen_ids[0]}\n" if count == 1 else "")
                         + "Daten aus der Dawum APi: https://dawum.de/ | Modul by Krokofant#0001")
    return wahlembed


class Dawum(commands.Cog):
    class DropdownButton(discord.ui.Select):
        def __init__(self, count):
            super().__init__(placeholder="Wähle ein Parlament aus!", min_values=1, max_values=1, options=[
                discord.SelectOption(label='Bundestag', description=' Bundestag'),
                discord.SelectOption(label='Baden-Württemberg',
                                     description=' Baden-Württemberg'),
                discord.SelectOption(label='Bayern', description=' Bayern'),
                discord.SelectOption(label='Berlin', description=' Berlin'),
                discord.SelectOption(label='Brandenburg',
                                     description=' Brandenburg'),
                discord.SelectOption(label='Bremen', description=' Bremen'),
                discord.SelectOption(label='Hamburg', description=' Hamburg'),
                discord.SelectOption(label='Hessen', description=' Hessen'),
                discord.SelectOption(label='Mecklenburg-Vorpommern',
                                     description=' Mecklenburg-Vorpommern'),
                discord.SelectOption(label='Niedersachsen',
                                     description=' Niedersachsen'),
                discord.SelectOption(label='Nordrhein-Westfalen (NRW)',
                                     description=' Nordrhein-Westfalen (NRW)'),
                discord.SelectOption(label='Rheinland-Pfalz',
                                     description=' Rheinland-Pfalz'),
                discord.SelectOption(label='Saarland', description=' Saarland'),
                discord.SelectOption(label='Sachsen', description=' Sachsen'),
                discord.SelectOption(label='Sachsen-Anhalt',
                                     description=' Sachsen-Anhalt'),
                discord.SelectOption(label='Schleswig-Holstein',
                                     description=' Schleswig-Holstein'),
                discord.SelectOption(label='Thüringen', description=' Thüringen'),
                discord.SelectOption(label='Europäisches Parlament',
                                     description=' Europäisches Parlament')])
            self.count = count

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.send_message(embed=umfrage_ausgeben(self.values[0].lower(), count=self.count))
            await interaction.channel.send(file=discord.File("data/output.png"))

    class DropdownUI(discord.ui.View):
        def __init__(self, count):
            super().__init__()
            self.add_item(Dawum.DropdownButton(count))

    def __init__(self, client):
        self.client = client
        self.lock = asyncio.Lock()

    @commands.command(aliases=["umfrage"])
    async def poll(self, ctx: commands.Context, count=1):
        """Gebe die aktuelle Wahlumfrage aus.
        Syntax: !poll<Umfragenzahl>
        Wähle anschließend ein Parlament aus!"""
        # The lock ensures that no plotting will be overwritten.
        async with self.lock:
            if count < 1:
                await ctx.send(embed=discord.Embed(
                    title="Error!", description="Count muss >= 1 sein"))
                return
            await ctx.send("Wähle ein Bundesland aus!", view=Dawum.DropdownUI(count))


def setup(client):
    client.add_cog(Dawum(client))
