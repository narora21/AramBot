# ARAM Bot Written by Nikhil Arora
# 12/26/2021
import discord
import logging
import os
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from dotenv import dotenv_values
from discord.ext import commands

from commands.query import QueryCommand
from constants import OPEN_AI_KEY, WEAVIATE_API_KEY, WEAVIATE_CLUSTER_URL, \
    DISCORD_TOKEN, DISCORD_GUILD_ID, TEST_GUILD_ID, TEST_MODE

VERSION = '2.0.0'

class AramBot:

    def __init__(self, config, version):
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        self.test_mode = config[TEST_MODE] == '1'
        self.open_ai_key = config[OPEN_AI_KEY]
        self.weaviate_api_key = config[WEAVIATE_API_KEY]
        self.weaviate_cluser_url = config[WEAVIATE_CLUSTER_URL]
        self.discord_token = config[DISCORD_TOKEN]
        self.test_guild_id = int(config[TEST_GUILD_ID])
        self.discord_guild_id = int(config[TEST_GUILD_ID]) if self.test_mode else int(config[DISCORD_GUILD_ID])
        self.logger = logging.getLogger(__name__)
        self.version = version
        self._init_commands(version)

    def _init_commands(self, version):
        self.query_command = QueryCommand(
            self.logger, 
            self.test_mode, 
            self.test_guild_id, 
            version,
            self.open_ai_key,
            self.weaviate_api_key,
            self.weaviate_cluser_url
        )

    def _create_log_file(self, guild_name):
        """Creates a log file in /logs/<guild_name>/runtime.log
        Returns this path if succesful
        """
        log_path = os.path.join('logs', self.guild.name)
        Path(log_path).mkdir(parents=True, exist_ok=True)
        log_filepath = os.path.join('logs', self.guild.name, 'runtime.log')        
        if not os.path.isfile(log_filepath):
            open(os.path.join(os.getcwd(), log_filepath), 'x').close()
        return log_filepath

    def _on_ready(self):
        self.guild = discord.utils.find(lambda g: g.id == self.discord_guild_id, self.bot.guilds)
        log_filepath = self._create_log_file(self.guild.name)
        handler = TimedRotatingFileHandler(
            filename=log_filepath, 
            when='D', 
            interval=1, 
            backupCount=90, 
            encoding='utf-8', 
            delay=False
        )
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        if self.test_mode:
            print('Running in Test Mode')
            self.logger.info("Running in Test Mode")
        print('Server started...')
        self.logger.info("{0} is connected to server {1} (id:{2})".format(
                self.bot.user, self.guild.name, self.guild.id
            )
        )

    def run(self):
        @self.bot.event
        async def on_ready():
            self._on_ready()

        @self.bot.command(name="query", help="Ask AramBot any question you like!")
        async def query(ctx, *args):
            await self.query_command.execute(ctx, args)

        self.bot.run(self.discord_token)


if __name__ == "__main__":
    config = dotenv_values('.env')
    AramBot(config, VERSION).run()