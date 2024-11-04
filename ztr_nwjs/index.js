const { spawn } = require('child_process');
const fs = require('fs');
const readline = require('readline');

const crlfDelay = Infinity;
const streamLines = (input) => readline.createInterface({ input, crlfDelay });
const fileLines = (file) => streamLines(fs.createReadStream(file));

const [title, fifoIn, fifoOut] = nw.App.argv;

const toElement = (dom) => {
    if (!Array.isArray(dom)) { return document.createTextNode(dom); }
    const [tagSpec, ...children] = dom;
    const [tag, ...classes] = tagSpec.split(".");
    const el = document.createElement(tag);
    el.className = classes.join(" ");
    for (const child of children) { el.appendChild(toElement(child)); }
    return el;
}

const fifoOutWriteStream = fs.createWriteStream(fifoOut);

const main = async() => {
    const app = document.getElementById("app");
    for await (const line of fileLines(fifoIn)) {
        const dom = JSON.parse(line);
        const el = toElement(dom);
        app.replaceChildren(el);
        const win = nw.Window.get();
        win.resizeTo(el.clientWidth + 40, el.clientHeight + 40);
        fifoOutWriteStream.write("\n");
    }
};

main();
