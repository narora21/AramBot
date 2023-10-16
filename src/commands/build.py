from . import Command

class BuildCommand(Command):
    def __init__(self, ctx, test_mode):
        self.ctx = ctx
        self.test_mode = test_mode		
            
    async def run(self):
        await self.ctx.send(f"Build command run")
        """
        if self.test_mode and ctx.guild.id != TEST_GUILD_ID:
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

        champ_name = champion[0].upper() + champion[1:].lower()
        await ctx.send(build_return_str(champ_name, soup))
        """
