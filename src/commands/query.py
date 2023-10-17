import weaviate

from .command import Command

"""
Query AramBot LLM with a question
"""

class QueryCommand(Command):
    command_tps = 5

    def __init__(self, logger, test_mode, test_guild_id, version, open_ai_key, weaviate_api_key, weaviate_cluster_url):
        self.version = version
        self.open_ai_key = open_ai_key
        self.weaviate_client = self._get_weaviate_client(weaviate_cluster_url, weaviate_api_key, open_ai_key)
        super(QueryCommand, self).__init__(self.command_tps, logger, test_mode, test_guild_id)

    def _get_weaviate_client(self, cluster_url, weaviate_api_key, open_ai_key):
        client = weaviate.Client(
            url = cluster_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key), 
            additional_headers = {
                "X-OpenAI-Api-Key": open_ai_key
            }
        )
        return client
    
    def _get_class_object(self, class_name):
        """Define a data collection (a "class" in Weaviate) to store objects in. 
        This is analogous to creating a table in relational (SQL) databases.
        If vectorizer is set to None, we must provide vectors ourselves
        The generative-openai config option for generative queries 
        """
        if not class_name:
            return None
        obj = {
            "class": class_name,
            "vectorizer": "text2vec-openai",  
            "moduleConfig": {
                "text2vec-openai": {},
                "generative-openai": {}  
            }
        }
        return obj

    async def _run(self, ctx, args):
        author = ctx.author.name
        query = " ".join(args)
        """
        query the cluster for context (conversation history and other relevant tables)
        give it to chat gpt
        send answer to server
        add query to conversation history in cluster
        """
        pass