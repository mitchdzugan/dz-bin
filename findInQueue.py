#!/usr/bin/env python3

from mpd import MPDClient
import dmenu
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
client = MPDClient()
client.timeout = 10
client.idletimeout = None
client.connect("localhost", 6600)

pl = client.playlistinfo()
status = client.status()
ref = {}
labels = []
for song in pl:
    label = song["title"] + " - " + song["artist"]
    ref[label] = song
    labels.append(label)
pos = int(status["song"])
for i in range(pos):
    mv = labels.pop(0)
    labels.append(mv)

song = dmenu.show(
    labels,
    command=f"{dir_path}/rofi-dmenu",
    prompt='Find Song in Queue',
    case_insensitive=True
)

print(["Song:", song])

if song in ref:
    client.play(ref[song]["pos"])
