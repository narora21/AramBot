# ARAM Bot Written by Nikhil Arora
# 12/26/2021
import os
import sys
import discord
import requests
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from discord.ext import commands

TEST_MODE = False
LOGGER = None

def log_msg(msg):
	global LOGGER
	print(msg)
	LOGGER.info(msg)

def load_champs():
	return

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

def get_summoner_spell(spell):
	summoner_spells = ["heal", "ghost", "barrier", "exhaust", "mark", "clarity", "flash", "teleport", "smite", "cleanse", "ignite"]
	title = BeautifulSoup(spell.img['title'], 'html.parser')
	name = title.b.text
	return name

def get_skill_key(skill):
	return skill.span.text

def get_all_skills(spells_and_skills):
	first_skill = 2
	while spells_and_skills[first_skill].find("img", class_="tip") and first_skill < len(spells_and_skills):
		first_skill += 1
	return spells_and_skills[first_skill], spells_and_skills[first_skill+1], spells_and_skills[first_skill+2]

def scrape_runes(soup):
	runes = soup.find_all("div", class_=lambda value: value and value.endswith("--active"))
	rune_titles = soup.find_all("div", class_="perk-page")
	primary_title = get_rune_tree_name(rune_titles[0].div.div.img['title'])
	secondary_title = get_rune_tree_name(rune_titles[1].div.div.img['title'])
	primary_runes = [runes[i].div.img['alt'] for i in range(4)]
	secondary_runes = [runes[i].div.img['alt'] for i in range(4,6)]
	stat_buffs = list(map(get_stat_buff_name, map(lambda tag: tag['title'], soup.find("div", class_="fragment-page").find_all("img", class_=lambda value: value and value.startswith("active")))))
	return primary_title, primary_runes, secondary_title, secondary_runes, stat_buffs

def scrape_spells(soup):
	spells_and_skills = soup.find_all("li", class_="champion-stats__list__item")
	spell1, spell2 = spells_and_skills[:2]
	spell_name1 = get_summoner_spell(spell1)
	spell_name2 = get_summoner_spell(spell2)
	return spell_name1, spell_name2

def scrape_skills(soup):
	spells_and_skills = soup.find_all("li", class_="champion-stats__list__item")
	skill1, skill2, skill3 = get_all_skills(spells_and_skills)
	skill_name1 = get_skill_key(skill1)
	skill_name2 = get_skill_key(skill2)
	skill_name3 = get_skill_key(skill3)
	return skill_name1, skill_name2, skill_name3

def scrape_items(soup):
	items_table = soup.find_all("tbody")[3]
	row = items_table.find('tr')
	starter_items = []
	core_items = []
	boot_items = []
	header = ""
	while row is not None:
		if row.find("th") is not None:
			header = row.th.text.lower().strip()
		items = row.find_all("li", class_="champion-stats__list__item tip")
		item_row = []
		for item in items:
			item_row.append(BeautifulSoup(item['title'], 'html.parser').b.text)
		if header == "starter items":
			starter_items.append(item_row)
		elif header == "recommended build":
			core_items.append(item_row)
		elif header == "boots":
			boot_items.append(item_row)
		row = row.find_next_sibling("tr")
	return starter_items, core_items, boot_items

def build_runes_str(soup):
	primary_title, primary_runes, secondary_title, secondary_runes, stat_buffs = scrape_runes(soup)
	prim_str = f"({primary_title}) {' + '.join(primary_runes)}"
	sec_str = f"({secondary_title}) {' + '.join(secondary_runes)}"
	bonus_str = f"(Bonus Stats) {' + '.join(stat_buffs)}"
	rune_str = f"{prim_str}\n{sec_str}\n{bonus_str}"
	return rune_str

def build_spells_str(soup):
	spell_name1, spell_name2 = scrape_spells(soup)
	spell_str = f"{spell_name1}, {spell_name2}"
	return spell_str

def build_skills_str(soup):
	skill_name1, skill_name2, skill_name3 = scrape_skills(soup)
	skill_str = f"{skill_name1} > {skill_name2} > {skill_name3}"
	return skill_str

def build_items_str(soup):
	starter_items, core_items, boot_items = scrape_items(soup)
	start_str = f"(Starter Items) {' > '.join(starter_items[0])}"
	core_str = f"(Core Items) {' > '.join(core_items[0])}"
	boot_str = f"(Boots) {' > '.join(boot_items[0])}"
	items_str = f"{start_str}\n{core_str}\n{boot_str}"
	return items_str

def build_return_str(champ_name, soup):
	header_str = f"Recommended build for {champ_name}:"
	rune_str = f"Runes:\n{build_runes_str(soup)}"
	item_str = f"Items:\n{build_items_str(soup)}"
	spell_str = f"Summoner Spells: {build_spells_str(soup)}"
	skill_str = f"Skill Level Up: {build_skills_str(soup)}"
	return f"```{header_str}\n{rune_str}\n\n{item_str}\n\n{spell_str}\n\n{skill_str}```"
	

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
		global LOGGER
		if TEST_MODE:
			GUILD = discord.utils.find(lambda g: g.id == TEST_GUILD_ID, bot.guilds)
		else:
			GUILD = discord.utils.find(lambda g: g.name == GUILD_NAME, bot.guilds)
		LOGGER = logging.getLogger(__name__)
		if not os.path.exists(f'logs/{GUILD_NAME}'):
			os.makedirs(f'logs/{GUILD_NAME}')
		handler = TimedRotatingFileHandler(filename=f'logs/{GUILD_NAME}/runtime.log', when='D', interval=1, backupCount=90, encoding='utf-8', delay=False)
		formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		LOGGER.addHandler(handler)
		LOGGER.setLevel(logging.INFO)
		if TEST_MODE:
			log_msg(f"Running in test mode")
		log_msg("{0} is connected to server {1} (id:{2})".format(bot.user, GUILD.name, GUILD.id))
		print("Command history:")

	@bot.command(name="mmr", help="Get your ARAM, Ranked Solo, and Normal mmr")
	async def mmr(ctx, *summoner_name):
		if TEST_MODE and ctx.guild.id != TEST_GUILD_ID:
			log_msg(f"Ignored command from non-test server: {ctx.guild.name} (id: {ctx.guild.id})")
			return
		summoner = " ".join(summoner_name)
		log_msg(f"{ctx.author} sent \"!mmr {summoner}\" in {ctx.guild}")
		# rate: 60 requests per minute
		nonlocal last_mmr_call
		t = time.time()
		if t - last_mmr_call < 1:
			await ctx.send("Error: Please limit requests to 1 per second")
			log_msg("Error: Please limit requests to 1 per second")
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

		aram_info = f"(ARAM) mmr: {aram_mmr}, rank: {aram_rank}, percentile: {aram_perc}"
		ranked_info = f"(Ranked Solo) mmr: {ranked_mmr}, rank: {ranked_rank}, percentile: {ranked_perc}"
		norm_info = f"(Normals) mmr: {norm_mmr}, rank: {norm_rank}, percentile: {norm_perc}"
		disclaimer = "None entries indicate there are not enough games played in the last 30 days"
		await ctx.send(f"```Data for {summoner}:\n{aram_info}\n{ranked_info}\n{norm_info}\n{disclaimer}```")

	@bot.command(name="build", help="Get op.gg recommended ARAM builds")
	async def build(ctx, champion, queue_type="aram"):
		if TEST_MODE and ctx.guild.id != TEST_GUILD_ID:
			log_msg(f"Ignored command from non-test server: {ctx.guild.name} (id: {ctx.guild.id})")
			return
		log_msg(f"{ctx.author} sent \"!build {champion} {queue_type}\" in {ctx.guild}")
		# rate: 60 requests per minute
		nonlocal last_build_call
		t = time.time()
		if t - last_build_call < 1:
			await ctx.send("Error: Please limit requests to 1 per second")
			log_msg("Error: Please limit requests to 1 per second")
			return
		last_build_call = t

		if queue_type.lower() in ['sr', 'norms', 'normals', 'norm', 'normal', 'summonersrift', 'summoners-rift']:
			await ctx.send("Error: This queue type is not supported yet")
			log_msg("Error: This queue type is not supported yet")
			return
		elif queue_type.lower() != "aram":
			await ctx.send(f"Error: Queue type invalid: {queue_type}")
			log_msg(f"Error: Queue type invalid: {queue_type}")
			return

		url = f"https://www.op.gg/aram/{champion}/statistics/450/build"
		headers = {'User-Agent': 'Mozilla/5.0'}
		response = requests.get(url=url, headers=headers)
		soup = BeautifulSoup(response.text, 'html.parser')
		if len(soup.find_all("div", class_="perk-page")) == 0:
			await ctx.send(f"Error: Champion not found: {champion}")
			log_msg(f"Error: Champion not found: {champion}")
			return
		#await ctx.send(url)

		champ_name = champion[0].upper() + champion[1:].lower()
		await ctx.send(build_return_str(champ_name, soup))

	bot.run(TOKEN)


if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1] == "test":
		print("Running in test mode")
		TEST_MODE = True
	main()