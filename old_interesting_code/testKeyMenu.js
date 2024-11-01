#!/usr/bin/env node

const { Menu } = require('./libKeyMenu.js');

Menu("TestMenu", ($) => $
  .cmd("a", "A button", "kitty")
  .cmd("b", "B button", "firefox")
  .sub("c", "C button", (($) => $
    .cmd("d", "D button", "setPlaylist.py")
    .cmd("e", "E button", "bringToWorkspace.py"))))
