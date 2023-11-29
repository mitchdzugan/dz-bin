#!/usr/bin/env fennel

(local view (require "fennel.view"))

(local dirname (: (. (debug.getinfo 1) :source) :match "@?(.*/)"))

(local m (require :libKeyMenu))

(m.make-config
  (fn []
    (m.title "dz system")
    ((m.sub "w" "workspaces")
     (fn []
       (m.cmd "ISO_Left_Tab" "move to last workspace" (.. dirname "goToLastWorkspace"))
       ))
    (m.cmd "k" "do echo" "echo hello world")
    ))
