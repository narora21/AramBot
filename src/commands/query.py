import weaviate

from .command import Command
from .exceptions import UserException
from .leagueUtils import get_latest_patch, update_cluster
from .constants import MAX_MESSAGE_LENGTH
from .constants import LEAGUE_CHAMPION_CLASS, LEAGUE_CHAMPION_SCHEMA, LEAGUE_VERSION
from .utils import get_app_config_value, update_app_config_value

"""
Query AramBot LLM with a question
"""

class QueryCommand(Command):
    command_tpm = 10
    default_char_limit = 200

    def __init__(self, logger, test_mode, test_guild_id, version, open_ai_key, weaviate_api_key, weaviate_cluster_url):
        self.version = version
        self.open_ai_key = open_ai_key
        self.weaviate_client = self._get_weaviate_client(weaviate_cluster_url, weaviate_api_key, open_ai_key)
        super(QueryCommand, self).__init__(self.command_tpm, logger, test_mode, test_guild_id)

    def _get_weaviate_client(self, cluster_url, weaviate_api_key, open_ai_key):
        client = weaviate.Client(
            url = cluster_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key), 
            additional_headers = {
                "X-OpenAI-Api-Key": open_ai_key
            }
        )
        return client
    
    def _get_base_prompt(self):
        return """
        You are AramBot, a helpful discord bot created by Nikhil Arora 
        that answers questions about League of Legends. 
        Keep your answer brief. It should be less than a paragraph.
        Your answer MUST be less than 2000 characters.
        Answer the following query given the context:
        """

    async def _run(self, ctx, args):
        # check daily transactions limit
        author = ctx.author.name
        query = " ".join(args)
        if len(query) > self.default_char_limit:
            error = f"Input query must be less than {self.default_char_limit} characters"
            print(error)
            self.logger.info(error)
            raise UserException(error)
        
        patch = get_latest_patch(self.logger)
        if patch != get_app_config_value(LEAGUE_VERSION):
            self.logger.info(f'Patch version out of date, updating to {patch}')
            await ctx.send(f"My information is out of date with the latest patch: {patch}, please wait while I update...")
            update_cluster(self.weaviate_client, patch, self.logger)
            update_app_config_value(LEAGUE_VERSION, patch)
        try:
            self.weaviate_client.schema.get(LEAGUE_CHAMPION_CLASS)
        except:
            self.logger.info("League champ class not found, updating cluster")
            await ctx.send(f"My information is out of date with the latest patch: {patch}, please wait while I update...")
            update_cluster(self.weaviate_client, patch, self.logger)
        prompt = self._get_base_prompt() + query
        result = (
            self.weaviate_client.query
            .get(LEAGUE_CHAMPION_CLASS, LEAGUE_CHAMPION_SCHEMA)
            .with_near_text({"concepts": [query]})
            .with_limit(1)
            .with_additional(['certainty'])
            .with_generate(grouped_task=prompt)
            .do()
        )
        answer = result['data']['Get'][LEAGUE_CHAMPION_CLASS][0]['_additional']['generate']['groupedResult']
        i = 0
        while i < len(answer):
            await ctx.send(answer[i:MAX_MESSAGE_LENGTH])
            i += MAX_MESSAGE_LENGTH