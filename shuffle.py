#!/usr/bin/python3

from mpd import MPDClient
import dmenu

client = MPDClient()
client.timeout = 10
client.idletimeout = None
client.connect("localhost", 6600)
client.shuffle()

