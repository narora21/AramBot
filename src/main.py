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