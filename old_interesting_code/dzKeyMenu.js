#!/usr/bin/env node

const { Menu, Key, MOD } = require('./libKeyMenu.js');

Menu("dz system", ($) => $
  .sub("w", "workspaces", ($) => $
    .cmd(Key.tab(MOD.SHIFT), "move to last workspace", `${__dirname}/goToLastWorkspace`)
    .cmd("F", "move to fresh workspace", `${__dirname}/sendToWorkspace.py -c 0 -f`)
    .cmd(Key[1](MOD.SHIFT), "move to workspace 1", "hyprctl dispatch movetoworkspace 1")
    .cmd(Key[2](MOD.SHIFT), "move to workspace 2", "hyprctl dispatch movetoworkspace 2")
    .cmd(Key[3](MOD.SHIFT), "move to workspace 3", "hyprctl dispatch movetoworkspace 3")
    .cmd(Key[4](MOD.SHIFT), "move to workspace 4", "hyprctl dispatch movetoworkspace 5")
    .cmd(Key[5](MOD.SHIFT), "move to workspace 5", "hyprctl dispatch movetoworkspace 5")
    .cmd(Key[6](MOD.SHIFT), "move to workspace 6", "hyprctl dispatch movetoworkspace 6")
    .cmd(Key[7](MOD.SHIFT), "move to workspace 7", "hyprctl dispatch movetoworkspace 7")
    .cmd(Key[8](MOD.SHIFT), "move to workspace 8", "hyprctl dispatch movetoworkspace 8")
    .cmd(Key[9](MOD.SHIFT), "move to workspace 9", "hyprctl dispatch movetoworkspace 9")
    .col()
    .cmd(Key.tab(), "last workspace", `${__dirname}/goToLastWorkspace`)
    .cmd("f", "fresh workspace", `${__dirname}/goToFreshWorkspace`)
    .cmd("1", "workspace 1", "hyprctl dispatch workspace 1")
    .cmd("2", "workspace 2", "hyprctl dispatch workspace 2")
    .cmd("3", "workspace 3", "hyprctl dispatch workspace 3")
    .cmd("4", "workspace 4", "hyprctl dispatch workspace 5")
    .cmd("5", "workspace 5", "hyprctl dispatch workspace 5")
    .cmd("6", "workspace 6", "hyprctl dispatch workspace 6")
    .cmd("7", "workspace 7", "hyprctl dispatch workspace 7")
    .cmd("8", "workspace 8", "hyprctl dispatch workspace 8")
    .cmd("9", "workspace 9", "hyprctl dispatch workspace 9")
    .col()
  )
  .col()
  // .sub("m", "music", ($) => $)
  .fn("b", "echo", () => { console.log("fn cmd") })
  .sub("c", "C button", (($) => $
    .cmd("d", "D button", "setPlaylist.py")
    .fn("e", "fn cmd 2", () => { console.log("fn cmd 2") }))))
