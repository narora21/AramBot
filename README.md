# AramBot

This bot is meant to invoke Riot APIs from discord to query useful information regarding our favorite League of Legends gamemode: ARAM. This bot should be able to query for MMR (provided by the na.whatismymmr.com API) as well as optimal ARAM builds for every champion (including runes, summoner spells, items, and ability level up order).

The supported commands will be:

!help
- returns helpful information about supported bot commands

!mmr {summoner-name}
- returns the Normal Summoners Rift, Ranked Solo, and ARAM mmr of the summoner

!winrate {summoner-name} (Not yet implemented)
- returns the Aram win rate of the summoner

!build {champion} (Partially implemented)
- returns the recommended ARAM build of the champion

