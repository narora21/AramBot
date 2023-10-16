from .command import Command

"""
Query AramBot LLM with a question
"""

class QueryCommand(Command):
    command_tps = 60

    def __init__(self, logger, test_mode, test_guild_id, version, open_ai_key, weaviate_api_key, weaviate_cluster_url):
        self.version = version
        self.open_ai_key = open_ai_key
        self.weaviate_api_key = weaviate_api_key
        self.weaviate_cluster_url = weaviate_cluster_url
        super(QueryCommand, self).__init__(self.command_tps, logger, test_mode, test_guild_id, version)

    def _whitelisted(author):
        pass

    async def _run(self, ctx, args):
        if not self._whitelisted(ctx.author):
            await ctx.send('You are not permitted to use this command, please contact Nikhil for permission')
            return
        query = " ".join(args)
        pass