# ARAM Bot Written by Nikhil Arora
# 12/26/2021
import os
import sys
import discord
import requests
import time
import logging
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from discord.ext import commands

TEST_MODE = False

def get_rune_tree_name(title):
	if "Sorcery" in title:
		return "Sorcery"
	if "Domination" in title:
		return "Domination"
	if "Precision" in title:
		return "Precision"
	if "Resolve" in title:
		return "Resolve"
	if "Inspiration" in title:
		return "Inspiration"
	return "None"

def get_stat_buff_name(title):
	if "Adaptive" in title:
		return "Adaptive"
	if "Attack Speed" in title:
		return "Attack Speed"
	if "Ability Haste" in title:
		return "Ability Haste"
	if "Armor" in title:
		return "Armor"
	if "Magic Resist" in title:
		return "Magic Resist"
	if "Health" in title:
		return "Health"
	return "None"

def main():
	load_dotenv()
	TOKEN = os.getenv('DISCORD_TOKEN')
	GUILD_NAME = os.getenv('DISCORD_GUILD')
	TEST_GUILD_ID = None
	if TEST_MODE:
		TEST_GUILD_ID = int(os.getenv('TEST_GUILD_ID'))

	bot = commands.Bot(command_prefix='!')
	GUILD = None
	last_mmr_call = time.time()
	last_build_call = time.time()

	@bot.event
	async def on_ready():
		nonlocal GUILD
		if TEST_MODE:
			GUILD = discord.utils.find(lambda g: g.id == TEST_GUILD_ID, bot.guilds)
		else:
			GUILD = discord.utils.find(lambda g: g.name == GUILD_NAME, bot.guilds)
		print("{0} is connected to server {1} (id:{2})".format(bot.user, GUILD.name, GUILD.id))
		logging.info("{0} is connected to server {1} (id:{2})".format(bot.user, GUILD.name, GUILD.id))
		print("Command history:")

	@bot.command(name="mmr", help="Get your ARAM, Ranked Solo, and Normal mmr")
	async def mmr(ctx, *summoner_name):
		if TEST_MODE and ctx.guild.id != TEST_GUILD_ID:
			print(f"Ignored command from non-test server: {ctx.guild.name} (id: {ctx.guild.id})")
			logging.info(f"Ignored command from non-test server: {ctx.guild.name} (id: {ctx.guild.id})")
			return
		summoner = " ".join(summoner_name)
		print(f"{ctx.author} sent \"!mmr {summoner}\" in {ctx.guild}")
		logging.info(f"{ctx.author} sent \"!mmr {summoner}\" in {ctx.guild}")
		# rate: 60 requests per minute
		nonlocal last_mmr_call
		t = time.time()
		if t - last_mmr_call < 1:
			await ctx.send("Error: Please limit requests to 1 per second")
			logging.info("Error: Please limit requests to 1 per second")
			return
		last_mmr_call = t

		response = requests.get(url=f"https://na.whatismymmr.com/api/v1/summoner?name={summoner}")
		data = response.json()
		if 'error' in data:
			await ctx.send(data['error']['message'])
			return

		aram_mmr = data['ARAM']['avg']
		aram_rank = data['ARAM']['closestRank']
		aram_perc = data['ARAM']['percentile']

		ranked_mmr = data['ranked']['avg']
		ranked_rank = data['ranked']['closestRank']
		ranked_perc = data['ranked']['percentile']

		norm_mmr = data['normal']['avg']
		norm_rank = data['normal']['closestRank']
		norm_perc = data['normal']['percentile']

		aram_info = f"ARAM:\tmmr: {aram_mmr}, rank: {aram_rank}, percentile: {aram_perc}"
		ranked_info = f"Ranked Solo:\tmmr: {ranked_mmr}, rank: {ranked_rank}, percentile: {ranked_perc}"
		norm_info = f"Normals:\tmmr: {norm_mmr}, rank: {norm_rank}, percentile: {norm_perc}"
		disclaimer = "None entries indicate there are not enough games played in the last 30 days"
		await ctx.send(f"{aram_info}\n{ranked_info}\n{norm_info}\n{disclaimer}")

	@bot.command(name="build", help="Get op.gg recommended ARAM builds")
	async def build(ctx, champion, queue_type="aram"):
		if TEST_MODE and ctx.guild.id != TEST_GUILD_ID:
			print(f"Ignored command from non-test server: {ctx.guild.name} (id: {ctx.guild.id})")
			logging.info(f"Ignored command from non-test server: {ctx.guild.name} (id: {ctx.guild.id})")
			return
		print(f"{ctx.author} sent \"!build {champion} {queue_type}\" in {ctx.guild}")
		logging.info(f"{ctx.author} sent \"!build {champion} {queue_type}\" in {ctx.guild}")
		# rate: 60 requests per minute
		nonlocal last_build_call
		t = time.time()
		if t - last_build_call < 1:
			await ctx.send("Error: Please limit requests to 1 per second")
			logging.info("Error: Please limit requests to 1 per second")
			return
		last_build_call = t

		if queue_type.lower() in ['sr', 'norms', 'normals', 'norm', 'normal', 'summonersrift', 'summoners-rift']:
			await ctx.send("Error: This queue type is not supported yet")
			logging.info("Error: This queue type is not supported yet")
			return
		elif queue_type.lower() != "aram":
			await ctx.send(f"Error: Queue type invalid: {queue_type}")
			logging.info(f"Error: Queue type invalid: {queue_type}")
			return

		url = f"https://www.op.gg/aram/{champion}/statistics/450/rune"
		headers = {'User-Agent': 'Mozilla/5.0'}
		response = requests.get(url=url, headers=headers)
		soup = BeautifulSoup(response.text, 'html.parser')

		runes = soup.find_all("div", class_=lambda value: value and value.endswith("--active"))
		rune_titles = soup.find_all("div", class_="perk-page")
		if len(rune_titles) == 0:
			await ctx.send(f"Error: Champion not found: {champion}")
			logging.info(f"Error: Champion not found: {champion}")
			return
		await ctx.send(url)
		primary_title = get_rune_tree_name(rune_titles[0].div.div.img['title'])
		secondary_title = get_rune_tree_name(rune_titles[1].div.div.img['title'])
		primary_runes = [runes[i].div.img['alt'] for i in range(4)]
		secondary_runes = [runes[i].div.img['alt'] for i in range(4,6)]
		stat_buffs = list(map(get_stat_buff_name, map(lambda tag: tag['title'], soup.find("div", class_="fragment-page").find_all("img", class_=lambda value: value and value.startswith("active")))))
		
		rune_str = f"{primary_title}: {' > '.join(primary_runes)}\n{secondary_title}: {' > '.join(secondary_runes)}\nBonus Stats: {' > '.join(stat_buffs)}"
		await ctx.send(rune_str)

	bot.run(TOKEN)


if __name__ == "__main__":
	logging.basicConfig(filename='arambot.log', level=logging.DEBUG)
	if len(sys.argv) == 2 and sys.argv[1] == "test":
		print("Running in test mode")
		logging.info(f"Running in test mode")
		TEST_MODE = True
	main()