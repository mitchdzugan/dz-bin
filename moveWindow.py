#!/usr/bin/python3

from argparse import ArgumentParser
import lib

appDesc = """
move hyprland client to specified ws
"""

parser = ArgumentParser(description=appDesc)
parser.add_argument(
        '-a',
        '--address',
        default=None,
        help='address of client to move. default focused'
)
parser.add_argument(
        '-w',
        '--ws',
        default='*',
        help='ws to move to. * for hidden. default *'
)
args = parser.parse_args()
address = args.address
ws = args.ws
if ws == "*":
        ws = "special"
if not address:
        activeWindow = lib.cmdJson('hyprctl activewindow -j')
        address = activeWindow["address"]
lib.moveWindow(address, ws)
