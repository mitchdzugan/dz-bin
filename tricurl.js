#!/usr/bin/env node

const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const { statSync, createReadStream, readFileSync, writeFileSync } = require('fs');

const __timeout_id__ = setTimeout(() => {}, 10000);
const finish = () => clearTimeout(__timeout_id__);

const tricurl = (src, { cacheTime=0, pupp=false, forceCache = false }) => {
  const path = `${__dirname}/state/tricurlcache/${pupp ? "p:" : ""}${btoa(src)}`;

  let readStream;
  try {
    const res = statSync(path);
    const delta = Date.now() - res.mtimeMs;
    if (delta < cacheTime || forceCache) {
      readStream = createReadStream(path);
    }
  } catch (e) {
  }

  if (readStream) {
    readStream.on('data', (data) => {
      console.log(data.toString('utf8'));
    });
    readStream.on('end', () => {
      finish();
    });
    return;
  }

  const getOut = pupp ? (
    async () => {
      try {
        const browser = await puppeteer.launch({
            headless: 'new'
        });
        const page = (await browser.pages())[0];
        const navDone = page.waitForNavigation({ waitUntil: 'load' });
        await page.goto(src);
        await navDone;
        const extractedText = await page.$eval(':root', (el) => el.outerHTML);
        await browser.close();
        return extractedText;
      } catch (e) {
        throw [1, e];
      }
    }
  )() : (
    new Promise((resolve, reject) => {
      const proc = spawn('curl', ['-s', src]);
      const outs = [];
      const errs = [];
      proc.stdout.on('data', (data) => {
        outs.push(data.toString("utf8"));
      });

      proc.stderr.on('data', (data) => {
        errs.push(data.toString("utf8"));
      });

      proc.on('close', (code) => {
        if (!code) {
          resolve(outs.join(""));
        } else {
          reject([code, errs.join("")]);
        }
      });
    })
  );

  getOut
    .then((out) => { writeFileSync(path, out); console.log(out); finish(); })
    .catch(([code, err]) => {
      if (!forceCache) {
        tricurl(src, { cacheTime, pupp, forceCache: true });
      } else if (pupp) {
        tricurl(src, { cacheTime, pupp: false, forceCache: true });
      } else {
        console.error(err);
        process.exit(code);
      }
    });
};

const main = () => {
  let i = 2;
  let cacheTime = 0;
  let pupp = false;
  let src = "";
  while (i < process.argv.length) {
    let isArg = 0;
    const word = process.argv[i];
    if (word.startsWith("-")) {
      for (const char of word.substr(1)) {
        if (char === 'p') {
          pupp = true;
        } else if (char === 'c') {
          isArg = 1;
          cacheTime = process.argv[i+1];
          if (cacheTime !== 'force') {
            cacheTime = parseInt(cacheTime, 10);
          }
        }
      }
    } else {
      src = word;
    }
    i += 1 + isArg;
  }
  tricurl(src, { cacheTime, pupp, forceCache: cacheTime === 'force' });
};

main();
