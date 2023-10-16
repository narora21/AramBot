from .command import Command

"""
Add a discord user to the whitelist to use the 
AramBot LLM via the query command
"""

class QueryCommand(Command):
    command_tps = 60

    def __init__(self, logger, test_mode, test_guild_id, version):
        self.version = version
        super(QueryCommand, self).__init__(self.command_tps, logger, test_mode, test_guild_id)

    async def _run(self, ctx, args):
        pass