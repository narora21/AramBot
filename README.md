# AramBot

This bot is meant to invoke 3rd party APIs and web scrapers to query useful information regarding our favorite League of Legends gamemode: ARAM and sent it right to your discord channel. This bot should be able to query for MMR (provided by the na.whatismymmr.com API) as well as optimal ARAM builds for every champion (including runes, summoner spells, items, and ability level up order).

The supported commands are:

!help
- returns helpful information about supported bot commands

!mmr {summoner-name}
- returns the Normal Summoners Rift, Ranked Solo, and ARAM mmr of the summoner

!winrate {summoner-name} (Not yet implemented)
- returns the Aram win rate of the summoner

!build {champion} {queue-type (default: aram)} (only aram implemented)
- returns the recommended ARAM build of the champion

## Setup
To run aram bot simply run:
```
python3 src/main.py
```