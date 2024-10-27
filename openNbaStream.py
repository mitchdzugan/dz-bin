#!/usr/bin/env python3

import dmenu
import os
import requests
from bs4 import BeautifulSoup

dir_path = os.path.dirname(os.path.realpath(__file__))

def getSoup(url):
    r = requests.get(url = url)
    return BeautifulSoup(r.text, 'html.parser')


soup = getSoup("https://links.nbabite.com/")
games_soup = soup.find(id="fixtures").find_all("a")
games = []
ref = {}
for game_soup in games_soup:
    href = game_soup.attrs['href']
    when = game_soup.find("span").text
    [away, home] = game_soup.find_all("strong")
    label = f"{away.text} @ {home.text} [{when}]"
    game = {}
    game["href"] = href
    game["label"] = label
    ref[label] = game
    games.append(game)

gameLabel = dmenu.show(
    map(lambda game: game["label"], games),
    command=f"{dir_path}/rofi-dmenu",
    prompt='Select Game',
    case_insensitive=True
)

if gameLabel in ref:
    game = ref[gameLabel]
    ref = {}
    soup = getSoup(f"https://links.nbabite.com{game['href']}")
    streams_soup = soup.find(id="streams")
    streamlinkrows = streams_soup.find("tbody").find_all("tr")
    links = []
    rank = 0
    for row in streamlinkrows:
        rank += 1
        link = row.find("a")
        rep = row.select_one(".text-center span.label")
        repText = ""
        if rep:
            for c in rep.attrs["class"]:
                if c == 'label-platinum':
                    repText = ""
                if c == 'label-gold-standard':
                    repText = ""
                if c == 'label-silver':
                    repText = ""
        href = link.attrs["href"]
        label = f"{rank}. {link.text} - {repText}"
        link = {}
        link["href"] = href
        link["label"] = label
        ref[label] = link
        links.append(link)
    linkLabel = dmenu.show(
        map(lambda link: link["label"], links),
        command=f"{dir_path}/rofi-dmenu",
        prompt='Select Stream',
        case_insensitive=True
    )
    if linkLabel in ref:
        link = ref[linkLabel]
        print(link["href"])
