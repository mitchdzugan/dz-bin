const [title] = nw.App.argv;
const windowConfig = {
    title,
    show_in_taskbar: false,
    frame: false, 
    transparent: true
};

nw.Window.open('index.html', windowConfig);
