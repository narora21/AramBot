# ARAM Bot Written by Nikhil Arora
# 12/26/2021
import os
import discord
import requests
import time
from html2image import Html2Image
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from discord.ext import commands

def main():
	load_dotenv()
	TOKEN = os.getenv('DISCORD_TOKEN')
	GUILD_ID = os.getenv('DISCORD_GUILD')

	bot = commands.Bot(command_prefix='!')
	GUILD = None
	last_mmr_call = time.time()
	last_build_call = time.time()

	@bot.event
	async def on_ready():
		nonlocal GUILD
		GUILD = discord.utils.find(lambda g: g.name == GUILD_ID, bot.guilds)
		print("{0} is connected to server {1} (id:{2})".format(bot.user, GUILD.name, GUILD.id))
		print("Command history:")

	@bot.command(name="mmr", help="Get your ARAM, Ranked Solo, and Normal mmr")
	async def mmr(ctx, summoner):
		print(f"{ctx.author} sent \"!mmr {summoner}\" in {ctx.guild}")
		# rate: 60 requests per minute
		nonlocal last_mmr_call
		t = time.time()
		if t - last_mmr_call < 1:
			await ctx.send("Please limit requests to 1 per second")
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
		print(f"{ctx.author} sent \"!build {champion} {queue_type}\" in {ctx.guild}")
		# rate: 60 requests per minute
		nonlocal last_build_call
		t = time.time()
		if t - last_build_call < 1:
			await ctx.send("Please limit requests to 1 per second")
			return
		last_build_call = t

		url = f"https://u.gg/lol/champions/aram/{champion}"
		sr_url = f"https://u.gg/lol/champions/{champion}/build"
		if queue_type.lower() in ['sr', 'norms', 'normals', 'norm', 'normal', 'summonersrift', 'summoners-rift']:
			url = sr_url
		elif queue_type.lower() != "aram":
			await ctx.send(f"Queue type invalid: {queue_type}")
			return

		await ctx.send(url)

		#chrome = "/bin/"
		#hti = Html2Image(browser_executable=chrome, custom_flags=['--virtual-time-budget=0', '--enable-heavy-ad-intervention'])
		#with BytesIO() as output:
		#	hti.screenshot(url=url, save_as=output)
		#	contents = output.getvalue()
		#	picture = discord.File(contents, f"{champion}-{queue_type}-build.png")
		#	await ctx.send(file=picture)


	bot.run(TOKEN)


if __name__ == "__main__":
	main()