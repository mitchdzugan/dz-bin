#!/usr/bin/env fennel

(local view (require :fennel.view))
(local json (require :dkjson))

(local color
       {:bg "#1e1e2e"
        :fg "#CDD6F4"
        :black "#45475A"
        :red "#F38BA8"
        :green "#A6E3A1"
        :yellow "#F9E2AF"
        :blue "#89B4FA"
        :magenta "#F5C2E7"
        :cyan "#94E2D5"
        :white "#BAC2DE"
        :bright {
          :black ""
          :red "#F38BA8"
          :green "#A6E3A1"
          :yellow "#F9E2AF"
          :blue ""
          :magenta ""
          :cyan ""
          :white ""}})

(local which-key-bin
       "/home/mitch/Projects/wlr-which-key/target/debug/wlr-which-key")

(local base-config
       {:font "Serious Sans Nerd Font Mono 12"
        :background (.. color.bg "77")
        :color color.bright.cyan
        :color_key color.bright.magenta
        :color_mod color.bright.blue
        :color_sep color.bright.black
        :color_and color.bright.yellow
        :color_cmd color.yellow
        :border (.. color.blue "77")
        :separator " : "
        :title_separator " / "
        :border_width 1
        :column_spacing 3
        :corner_radius 0
        :padding 35
        :anchor "center"})

(local global-bound {})
(fn bound [k] (. global-bound k))
(fn binding [...]
  (let [args [...] prev {}]
    (fn [f]
      (for [i 1 (length args) 2]
        (tset prev (. args i) (. global-bound (. args i)))
        (tset global-bound (. args i) (. args (+ i 1))))
      (f)
      (for [i 1 (length args) 2]
        (tset global-bound (. args i) (. prev (. args i)))))))

(fn make-config [f]
  (let [config (collect [k v (pairs base-config)] k v)]
    (tset config :menu {:newcols [] :items []})
    ((binding :config config :path [] :menu config.menu) f)
    (print (json.encode config))))

(fn title [s]
  (let [menu (bound :menu)]
    (tset menu :title s)))

(fn add-item [k desc var_]
  (let [[key after] (if (= "table" (type k))
                        [k.key k.after]
                        [k (fn [])])
        menu (bound :menu)]
    (tset menu :items (+ (length menu.items) 1) {: key : desc :var var_})
    (after)))

(fn cmd [k desc cmd]
  (add-item k desc {:cmd cmd}))

(fn sub [k desc]
  (fn [f]
    (let [path (bound :path)
          menu (bound :menu)
          submenu {:rec {:newcols [] :items []}}]
      (add-item k desc submenu)
      (tset path (+ (length path) 1) (length menu.items))
      ((binding :menu submenu.rec) f)
      (table.remove path))))

(fn col []
  (let [menu (bound :menu)]
    (tset menu :newcols (+ (length menu.newcols) 1) (+ (length menu.items) 1))))

(fn main []
  (print "main"))

(if (not (pcall debug.getlocal 6 1)) (main))

{:make-config make-config
 :title title
 :cmd cmd
 :sub sub
}
