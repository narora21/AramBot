import json

from .command import Command
from .constants import USERNAME, PERMISSIONS, COMMANDS, ALLOW, DENY, \
    COMMAND, LEVEL, ALL_LEVEL, LIMITED_LEVEL, NONE_LEVEL

"""
Add a discord user to the whitelist to use a
command that requires permission to invoke
"""

class WhitelistCommand(Command):
    command_tps = 60
    usage_str=f"""
        Usage: !whitelist {COMMAND} <username> <command> <{ALLOW}/{DENY}>
               !whitelist {LEVEL} <username> <{ALL_LEVEL}/{LIMITED_LEVEL}/{NONE_LEVEL}>
    """

    def __init__(self, logger, test_mode, test_guild_id, version):
        self.version = version
        super(WhitelistCommand, self).__init__(self.command_tps, logger, test_mode, test_guild_id)
    
    async def _run_command_change(self, ctx, args):
        """
        args[0] - subcommand name
        args[1] - discord username
        args[2] - command name
        args[3] - allow/deny (optional)
        """
        if len(args) < 3 or len(args) > 4:
            await ctx.send(self.usage_str)
            return
        username = args[1]
        command = args[2]
        allow = True
        if len(args) == 4:
            if args[3].lower() not in [ALLOW, DENY]:
                error = f"Error: Option not recognized: {args[3]}, choose from [{ALLOW}, {DENY}]"
                print(error)
                self.logger.info(error)
                await ctx.send(error)
                return
            allow = args[3].lower() == ALLOW
        whitelist = None
        with open(self.whitelist_file_path, 'r') as whitelist_file:
            whitelist = json.loads(whitelist_file.read())
            for user in whitelist:
                if user[USERNAME] == username:
                    if allow and command not in user[COMMANDS]:
                        user[COMMANDS].append(command)
                    elif not allow and command in user[COMMANDS]:
                        user[COMMANDS].remove(command)
                    break
        with open(self.whitelist_file_path, 'w') as whitelist_file:
            whitelist_file.write(json.dumps(whitelist))
    
    async def _run_level_change(self, ctx, args):
        """
        args[0] - subcommand name
        args[1] - discord username
        args[2] - permission level
        """
        if len(args) != 3:
            await ctx.send(self.usage_str)
            return
        username = args[1]
        level = args[2]
        if level not in [ALL_LEVEL, LIMITED_LEVEL, NONE_LEVEL]:
            error = f"Error: Option not recognized: {level}, choose from [{ALL_LEVEL},{LIMITED_LEVEL},{NONE_LEVEL}]"
            print(error)
            self.logger.info(error)
            await ctx.send(error)
            return
        whitelist = None
        with open(self.whitelist_file_path, 'r') as whitelist_file:
            whitelist = json.loads(whitelist_file.read())
            for user in whitelist:
                if user[USERNAME] == username:
                    user[PERMISSIONS] = level
                    break
        with open(self.whitelist_file_path, 'w') as whitelist_file:
            whitelist_file.write(json.dumps(whitelist))

    async def _run(self, ctx, args):
        if len(args) < 3:
            await ctx.send(self.usage_str)
            return
        subcommand = args[0]
        if subcommand not in [COMMAND, LEVEL]:
            await ctx.send(self.usage_str)
            return
        if subcommand == COMMAND:
            await self._run_command_change(ctx, args) 
        else:
            await self._run_level_change(ctx, args)
