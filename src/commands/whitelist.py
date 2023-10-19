import json

from .command import Command
from .exceptions import UserException
from .constants import USERNAME, PERMISSIONS, COMMANDS, ALLOW, DENY, \
    COMMAND, LEVEL, ALL_LEVEL, LIMITED_LEVEL, NONE_LEVEL, LIMITS, NAME

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
    
    async def _run_command_change(self, args):
        """
        args[0] - subcommand name
        args[1] - discord username
        args[2] - command name
        args[3] - allow/deny (optional)
        """
        if len(args) < 3 or len(args) > 4:
            raise UserException(self.usage_str)
        username = args[1]
        command = args[2]
        allow = True
        if len(args) == 4:
            if args[3].lower() not in [ALLOW, DENY]:
                error = f"Option not recognized: {args[3]}, choose from [{ALLOW}, {DENY}]"
                print(f"UserException: {error}")
                self.logger.info(f"UserException: {error}")
                raise UserException(error)
            allow = args[3].lower() == ALLOW
        whitelist = None
        with open(self.whitelist_file_path, 'r') as whitelist_file:
            whitelist = json.loads(whitelist_file.read())
            for user in whitelist:
                if user[USERNAME] == username:
                    cmd_names = list(map(lambda cmd: cmd[NAME], user[COMMANDS]))
                    if allow and command not in cmd_names:
                        user[COMMANDS].append({NAME: command, LIMITS: {}})
                    elif not allow and command in cmd_names:
                        updated_cmds = []
                        for cmd in user[COMMANDS]:
                            if cmd[NAME] != command:
                                updated_cmds.append(cmd)
                        user[COMMANDS] = updated_cmds
                    break
        with open(self.whitelist_file_path, 'w') as whitelist_file:
            whitelist_file.write(json.dumps(whitelist))
    
    async def _run_level_change(self, args):
        """
        args[0] - subcommand name
        args[1] - discord username
        args[2] - permission level
        """
        if len(args) != 3:
            raise UserException(self.usage_str)
        username = args[1]
        level = args[2]
        if level not in [ALL_LEVEL, LIMITED_LEVEL, NONE_LEVEL]:
            error = f"Option not recognized: {level}, choose from [{ALL_LEVEL},{LIMITED_LEVEL},{NONE_LEVEL}]"
            print(f"UserException: {error}")
            self.logger.info(f"UserException: {error}")
            raise UserException(error)
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
            await self._run_command_change(args) 
        else:
            await self._run_level_change(args)
