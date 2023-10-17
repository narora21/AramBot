from abc import ABC, abstractmethod
import time
import os
import json

from .constants import USERNAME, PERMISSIONS, COMMANDS, \
    ALL_LEVEL, LIMITED_LEVEL, NONE_LEVEL
from .utils import timer

"""
Abstract class to be implemented by any command
Any command sub-classimplementing this class should implement  
the _run(self, ctx, *args) method. When the command sub-class
is meant to be executed, it should be run by calling the
execute(self, ctx, *args) method
"""

class Command(ABC):
    whitelist_file_path = os.path.join(os.getcwd(), os.path.join('data', 'whitelist.json'))
    last_run_time = 0

    def __init__(self, tps, logger, test_mode, test_guild_id, requires_whitelist=True):
        if tps <= 0:
            raise Exception("TPS cannot be less than or equal to zero")
        self.tps = tps
        self.requires_whitelist = requires_whitelist
        self.logger = logger
        Command.logger = logger
        self.test_mode = test_mode
        self.test_guild_id = test_guild_id

    def _get_logger():
        return Command.logger
    
    def _get_command_name(self):
        name = self.__class__.__name__
        if 'Command' in name:
            return name[:name.find('Command')].lower()
        return name.lower()
    
    def _whitelisted(self, author):
        """Check if a discord user is whitelisted for this command"""
        if not self.requires_whitelist:
            return True
        with open(self.whitelist_file_path, 'r') as whitelist_file:
            whitelist = json.loads(whitelist_file.read())
            for user in whitelist:
                if user[USERNAME] == author.name:
                    permissions = user[PERMISSIONS]
                    if permissions == NONE_LEVEL:
                        return False
                    if permissions == ALL_LEVEL:
                        return True
                    if permissions == LIMITED_LEVEL:
                        return self._get_command_name() in user[COMMANDS]
                    else:
                        raise Exception(f"Error: Invalid permissions level: {permissions}, for user: {author.name}")
        return False

    @abstractmethod
    async def _run(self, ctx, args):
        """Abstract method that every command implements to 
        specify what the command should do when executed
            ctx: Bot context
            args: Command line arguments from server
        """
        pass

    @timer(_get_logger)
    async def execute(self, ctx, args):
        """Runs the bot command along with useful wrappers
            ctx: Bot context
            args: Command line arguments from server
        """
        received_msg = f"Received a {self._get_command_name()} from {ctx.author} in {ctx.guild} with args: {args}"
        print(received_msg)
        self.logger.info(received_msg)
        if self.test_mode and ctx.guild.id != self.test_guild_id:
            self.logger.info(f"Ignored command from non-test server: {ctx.guild.name} (id: {ctx.guild.id})")
            return
        try:
            if not self._whitelisted(ctx.author):
                await ctx.send('You are not permitted to use this command, please contact Nikhil for permission')
                return
        except Exception as e:
            error = f'Could not load whitelist: {e}'
            print(error)
            self.logger.error(error)
            await ctx.send("Error: An internal error occurred :(")
            return
        time_since_last_run = time.time() - self.last_run_time
        if time_since_last_run < 60 / self.tps:
            await ctx.send("Error: Please wait before sending too many requests")
            return
        self.last_run_time = time.time()
        try:
            await self._run(ctx, args)
        except Exception as e:
            error = f'An error ocurred while running the command: {e}'
            print(error)
            self.logger.error(error)
            await ctx.send("Error: An internal error occurred :(")
            return
