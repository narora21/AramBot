import requests
import json
import os
import time

from .constants import CHAMPIONS_PATH, CHAMPION_PATH, ITEMS_PATH, VERSIONS_PATH, \
    LEAGUE_CHAMPION_CLASS
from .constants import NAME, TITLE, SKINS, LORE, ALLYTIPS, ENEMYTIPS, TAGS, \
    STATS, PASSIVE, QABILITY, WABILITY, EABILITY, RABILITY
from .constants import ABILITY_NAME, ABILITY_DESCRIPTION, ABILITY_COOLDOWN, \
    ABILITY_RESOURCE, ABILITY_MAX_RANK, ABILITY_RANGE, ABILITY_TIP

"""
Data endpoints
"""
versions_ep = "https://ddragon.leagueoflegends.com/api/versions.json"
champions_ep = "http://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
champion_ep = "http://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion/{champion}.json"
items_ep = "http://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/item.json"
build_ep = "https://u.gg/lol/champions/{champion}/build"

def download(endpoint, dest, logger=None):
    if logger:
        logger.info(f"Downloading data from {endpoint}")
    if not os.path.exists(dest):
        os.makedirs(dest)
    filename = endpoint.split('/')[-1].replace(" ", "_")
    file_path = os.path.join(dest, filename)
    response = requests.get(endpoint, stream=True)
    if response.ok:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:
        error = f"Download failed for {endpoint}"
        print(error)
        if logger:
            logger.error(error)
        raise Exception(error)
    return file_path

"""
Get League data
"""
def get_latest_patch(logger=None):
    """Downloads list of patches and returns the latest patch
    """
    path = download(versions_ep, VERSIONS_PATH, logger)
    with open(path, 'r') as versions:
        return json.loads(versions.read())[0].strip()

def get_champions_data(patch, logger=None):
    """Downloads data for all champions for a given patch
    """
    return download(champions_ep.format(patch=patch), CHAMPIONS_PATH, logger)

def get_champion_data(champion, patch, logger=None):
    """Downloads data for a specific champion for a given patch
    """
    return download(champion_ep.format(patch=patch, champion=champion), CHAMPION_PATH.format(champion=champion), logger)

def get_items_data(patch, logger=None):
    """Downloads data for all items for a given patch
    """
    return download(items_ep.format(patch=patch), ITEMS_PATH, logger)

"""
Vector DB Cluster Operations
"""
def get_class_object_schema(class_name):
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

def scrape_build(champion, logger=None):
    pass

def format_spell(spells, num):
    if len(spells) <= num:
        return ""
    spell = spells[num]
    name = spell.get('name')
    description = spell.get('description')
    cooldownBurn = spell.get('cooldownBurn')
    resource = spell.get('resource')
    maxrank = spell.get('maxrank')
    rangeBurn = spell.get('rangeBurn')
    tooltip = spell.get('tooltip')
    effectBurn = spell.get('effectBurn')
    vars = spell.get('vars')
    if tooltip is not None:
        if effectBurn is not None:
            for i in range(len(effectBurn)):
                if effectBurn[i] is not None and f'{{{{ e{i} }}}}' in tooltip:
                    tooltip = tooltip.replace(f'{{{{ e{i} }}}}', effectBurn[i])
        if vars is not None:
            for var in vars:
                if "key" in var and f'{{{{ {var["key"]} }}}}' in tooltip:
                    tooltip = tooltip.replace(f'{{{{ {var["key"]} }}}}')
    spell_props = {
        ABILITY_NAME: name,
        ABILITY_DESCRIPTION: description,
        ABILITY_COOLDOWN: cooldownBurn,
        ABILITY_RESOURCE: resource,
        ABILITY_MAX_RANK: maxrank,
        ABILITY_RANGE: rangeBurn,
        ABILITY_TIP: tooltip
    }
    return json.dumps(spell_props)
        

    

def get_champ_props(champ_data):
    skins = ", ".join(list(map(lambda skin: skin["name"], champ_data['skins'])))
    tags = ", ".join(champ_data['tags'])
    stats = json.dumps(champ_data['stats'])
    spells = champ_data['spells']
    q_ability = format_spell(spells, 0)
    w_ability = format_spell(spells, 1)
    e_ability = format_spell(spells, 2)
    r_ability = format_spell(spells, 3)
    passive = champ_data['passive']['name'] + ': ' + champ_data['passive']['description']
    props = {
        NAME: champ_data['name'],
        TITLE: champ_data['title'],
        SKINS: skins,
        LORE: champ_data['lore'],
        ALLYTIPS: ' '.join(champ_data['allytips']),
        ENEMYTIPS: ' '.join(champ_data['enemytips']),
        TAGS: tags,
        STATS: stats,
        PASSIVE: passive,
        QABILITY: q_ability,
        WABILITY: w_ability,
        EABILITY: e_ability,
        RABILITY: r_ability
    }
    return props

def add_champs_to_cluster(client, champ_objs):
    with client.batch as batch:
        for champ in champ_objs:
            batch.add_data_object(
                data_object=champ,
                class_name=LEAGUE_CHAMPION_CLASS
            )

def delete_class(client, class_name):
    client.schema.delete_class(class_name)

def update_cluster(client, patch, logger=None):
    delete_class(client, LEAGUE_CHAMPION_CLASS)
    champion_class = get_class_object_schema(LEAGUE_CHAMPION_CLASS)
    logger.info('Creating {LEAGUE_CHAMPION_CLASS} class in cluster')
    client.schema.create_class(champion_class)
    logger.info('Downloading champions data')
    champs_path = get_champions_data(patch, logger)
    champ_objs = []
    with open(champs_path, 'r', encoding="utf8") as champs_file:
        champions_data = json.loads(champs_file.read())["data"]
        for champion in champions_data:
            logger.info(f'Downloading data for {champion}')
            champ_path = get_champion_data(champion, patch, logger)
            with open(champ_path, 'r', encoding="utf8") as champ_file:
                champion_data = json.loads(champ_file.read())["data"][champion]
                champ_objs.append(get_champ_props(champion_data))
            time.sleep(0.1) # 100 ms
    add_champs_to_cluster(client, champ_objs)

