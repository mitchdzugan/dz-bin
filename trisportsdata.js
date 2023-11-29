#!/usr/bin/env node

const { spawn } = require('child_process');
const { statSync, readFileSync, writeFileSync } = require('fs');
const { JSDOM } = require('jsdom')

const timems = (spec) => (
  0
  + ((spec.ms || 0) * 1)
  + ((spec.s  || 0) * 1 * 1000)
  + ((spec.m  || 0) * 1 * 1000 * 60)
  + ((spec.h  || 0) * 1 * 1000 * 60 * 60)
  + ((spec.d  || 0) * 1 * 1000 * 60 * 60 * 24)
  + ((spec.M  || 0) * 1 * 1000 * 60 * 60 * 24 * 30)
  + ((spec.y  || 0) * 1 * 1000 * 60 * 60 * 24 * 365)
);

const tricurl = (src, cacheTime=timems({ M: 1 })) => new Promise(
    (resolve, reject) => {
      const proc = spawn(`${__dirname}/tricurl.js`, ["-pc", cacheTime, src]);
      const outs = [];
      const errs = [];
      proc.stdout.on('data', (data) => {
        outs.push(data.toString("utf8"));
      });

      proc.stderr.on('data', (data) => {
        errs.push(data.toString("utf8"));
      });

      proc.on('close', (code) => {
        const out = outs.join("");
        !code ? resolve(out) : reject({ code, out, err: errs.join("") });
      });
    }
);

const yahoo = (league) => `https://sports.yahoo.com/${league}/scoreboard`;
const sportsData = {
  links: {
    nba: (Y, M, D) => `https://www.espn.com/nba/scoreboard/_/date/${Y}${M}${D}`,
    wnba: (Y, M, D) => `https://www.espn.com/wnba/scoreboard/_/date/${Y}${M}${D}`,
  },
  update: () => {
    const d = new Date();
    const Y = d.getFullYear();
    const M = ((d.getMonth() + 1) % 12) || 12;
    const D = d.getDate();
    tricurl(sportsData.links.nba(Y, M, D), timems({ m: 5 }))
      .then((html) => {
        const { window: { document: htmlDoc } } = new JSDOM(html);
        const games = htmlDoc.querySelectorAll(
          "section.Scoreboard"
        );
        console.log(games.length);
        for (const game of games) {
          const data = {};
          const overview = game.querySelector('.ScoreboardScoreCell__Overview');
          data.time = overview.querySelector('.ScoreCell__Time').innerHTML;
          console.log(data);
        }
      });
  },
};

const main = () => {
  sportsData.update();
};

main();
