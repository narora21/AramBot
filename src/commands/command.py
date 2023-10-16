from abc import ABC, abstractmethod
import time

"""
Abstract class to be implemented by any command
Any command sub-classimplementing this class should implement  
the _run(self, ctx, *args) method. When the command sub-class
is meant to be executed, it should be run by calling the
execute(self, ctx, *args) method
"""

class Command(ABC):
    last_run_time = 0

    def __init__(self, tps, logger, test_mode, test_guild_id):
        if tps <= 0:
            raise Exception("TPS cannot be less than or equal to zero")
        self.tps = tps
        self.logger = logger
        self.test_mode = test_mode
        self.test_guild_id = test_guild_id

    @abstractmethod
    async def _run(self, ctx, args):
        """Abstract method that every command implements to 
        specify what the command should do when executed
            ctx: Bot context
            args: Command line arguments from server
        """
        pass

    async def execute(self, ctx, args):
        """Runs the bot command along with useful wrappers
            ctx: Bot context
            args: Command line arguments from server
        """
        received_msg = f"Received a {self.__class__.__name__} from {ctx.author} in {ctx.guild} with args: {args}"
        print(received_msg)
        self.logger.info(received_msg)
        if self.test_mode and ctx.guild.id != self.test_guild_id:
            self.logger.info(f"Ignored command from non-test server: {ctx.guild.name} (id: {ctx.guild.id})")
            return
        time_since_last_run = time.time() - self.last_run_time
        if time_since_last_run < 60 / self.tps:
            await ctx.send("Please wait before sending too many requests")
            return
        self.last_run_time = time.time()
        await self._run(ctx, args)
