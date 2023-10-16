from .command import Command
import requests

"""
Command to get a user's League of Legends mmr for
ARAM, Ranked Solo, and Normal Summoner Rift queues
"""

class MMRCommand(Command):
    command_tps = 60

    def __init__(self, logger, test_mode, test_guild_id, version):
        self.version = version
        super(MMRCommand, self).__init__(self.command_tps, logger, test_mode, test_guild_id)

    def _build_user_agent(self):
        return f'discord:AramBot:{self.version}'

    async def _run(self, ctx, args):
        if len(args) < 1:
            await ctx.send("Please provide a summoner name")
            return
        summoner = " ".join(args)
        headers = {'User-Agent': self._build_user_agent()}
        url = f'https://na.whatismymmr.com/api/v1/summoner?name={summoner}'
        
        response = requests.get(url, headers=headers)
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
        await ctx.send(f"```Data for {summoner}:\n{aram_info}\n{ranked_info}\n{norm_info}\n\n{disclaimer}```")

