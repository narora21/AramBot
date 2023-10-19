# Whitelist keys
USERNAME='username'
PERMISSIONS='permissions'
COMMANDS='commands'
NAME='name'
LIMITS='limits'
ALLOW='allow'
DENY='deny'
COMMAND='command'
LEVEL='level'
ALL_LEVEL='all'
LIMITED_LEVEL='limited'
NONE_LEVEL='none'

# Discord constants
MAX_MESSAGE_LENGTH=2000

# App Config keys
LEAGUE_VERSION = 'latest_league_version'

# Data destinations
import os
VERSIONS_PATH = os.path.join(os.getcwd(), os.path.join('data', 'versions'))
CHAMPIONS_PATH = os.path.join(os.getcwd(), os.path.join('data', 'champions'))
CHAMPION_PATH = os.path.join(os.getcwd(), os.path.join('data', 'champion', '{champion}'))
ITEMS_PATH = os.path.join(os.getcwd(), os.path.join('data', 'items'))

# Vector database cluster
LEAGUE_CHAMPION_CLASS = 'LeagueChampions'

# Champion object properties
NAME='name'
TITLE='title'
SKINS='skins'
LORE='lore'
ALLYTIPS='ally_tips'
ENEMYTIPS='enemy_tips'
TAGS='tags'
STATS='stats'
PASSIVE='passive'
QABILITY='q_ability'
WABILITY='w_ability'
EABILITY='e_ability'
RABILITY='r_ultimate_ability'
LEAGUE_CHAMPION_SCHEMA=[
    NAME, TITLE, SKINS, LORE, ALLYTIPS, ENEMYTIPS,
    TAGS, STATS, PASSIVE, QABILITY, WABILITY, EABILITY, RABILITY
]

# Ability object properties
ABILITY_NAME='ability_name'
ABILITY_DESCRIPTION='ability_description'
ABILITY_COOLDOWN='ability_cooldown_per_rank'
ABILITY_RESOURCE='ability_resource'
ABILITY_MAX_RANK='ability_max_rank'
ABILITY_RANGE='ability_range_per_rank'
ABILITY_TIP='ability_tip'
