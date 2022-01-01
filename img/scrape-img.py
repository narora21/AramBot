from bs4 import BeautifulSoup
from pathlib import Path
import requests
import urllib
import os

def get_soup(url):
	headers = {'User-Agent': 'Mozilla/5.0'}
	response = requests.get(url=url, headers=headers)
	soup = BeautifulSoup(response.text, 'html.parser')
	return soup

# Scrape Runes Icons
def scrape_runes():
	print("Scraping Runes...")
	url = "https://leagueoflegends.fandom.com/wiki/Category:Rune_icons"
	soup = get_soup(url)
	img_tags = soup.find_all("img", alt=lambda value: value and value.endswith("rune.png"))
	links = [img['src'] for img in img_tags]
	names = [img['alt'] for img in img_tags]
	for i in range(len(links)):
		print(links[i])
		f, h = urllib.request.urlretrieve(links[i], f"{os.path.dirname(os.path.abspath(__file__))}/runes/{names[i]}")
		print(f)
	print("Done")

# Scrape Item Icons:
def scrape_items():
	pass

# Scrape Spell Icons
def scrape_spells():
	pass

# Scrape Skill Icons
def scrape_skills():
	pass

if __name__ == "__main__":
	scrape_runes()