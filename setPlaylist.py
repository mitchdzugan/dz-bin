#!/usr/bin/env python3

from mpd import MPDClient
import dmenu
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
client = MPDClient()
client.timeout = 10
client.idletimeout = None
client.connect("localhost", 6600)

pls = client.listplaylists()
ref = {}
for pl in pls:
    ref[pl["playlist"]] = pl

pl = dmenu.show(
    map(lambda pl: pl["playlist"], pls),
    command=f"{dir_path}/rofi-dmenu",
    prompt='Set Playlist',
    case_insensitive=True
)

if pl in ref:
    client.clear()
    client.load(pl)
    client.shuffle()
    client.repeat(1)
    client.play(0)
