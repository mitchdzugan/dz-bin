#!/usr/bin/env python3

from mpd import MPDClient
import dmenu

client = MPDClient()
client.timeout = 10
client.idletimeout = None
client.connect("localhost", 6600)

status = client.status()
elapsed = float(status["elapsed"])
pos = int(status["song"])
print(elapsed)
if elapsed < 2:
    if pos < 1:
        pl = client.playlistinfo()
        client.play(len(pl) - 1)
    else:
        client.play(pos - 1)
else:
    client.play(pos)

