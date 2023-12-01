#!/usr/bin/env node

const { spawn } = require('child_process');
const { statSync, readFileSync, writeFileSync } = require('fs');
const { JSDOM } = require('jsdom')
const path = require('path');

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

const makeGameId= (league, Y, M, D, away, home, extra="") => (
  `${league}:${Y}:${M}:${D}:${away}:${home}:${extra}`
);

const parseGameId = (gameId) => {
  const [league, Y_, M_, D_, away, home, extra = ""] = gameId.split(":");
  return {
    league,
    Y: parseInt(Y_, 10),
    M: parseInt(M_, 10),
    D: parseInt(D_, 10),
    away,
    home,
    extra,
  }
};

const sportsData = {
  links: {
    nba: (Y, M, D) => `https://www.espn.com/nba/scoreboard/_/date/${Y}${M}${D}`,
    wnba: (Y, M, D) => `https://www.espn.com/wnba/scoreboard/_/date/${Y}${M}${D}`,
  },
  curr: { nba: {} },
  update: async () => {
    const d = new Date();
    const Y = d.getFullYear();
    const M = ((d.getMonth() + 1) % 12) || 12;
    const D = d.getDate();
    await tricurl(sportsData.links.nba(Y, M, D), 0)
      .then((html) => {
        const { window: { document: htmlDoc } } = new JSDOM(html);
        const games = htmlDoc.querySelectorAll(
          "section.Scoreboard"
        );
        for (const game of games) {
          const data = {};
          let state = 'unknown';
          if (!!game.querySelector('.ScoreboardScoreCell--pre')) {
            state = 'pre';
          } else if (!!game.querySelector('.ScoreboardScoreCell--in')) {
            state = 'in-progress';
          } else if (!!game.querySelector('.ScoreboardScoreCell--post')) {
            state = 'post';
          }
          data.state = state;
          const someEspnGameHref = game
            .querySelector('.Scoreboard__Callouts a.AnchorLink')
            .getAttribute('href');
          const gameId_rx = (/.*\/gameId\/(.*)/).exec(someEspnGameHref);
          data.espnGameId = gameId_rx && gameId_rx[1];
          const overview = game.querySelector('.ScoreboardScoreCell__Overview');
          data.time = overview.querySelector('.ScoreCell__Time').innerHTML;
          const teams = game.querySelectorAll('ul.ScoreboardScoreCell__Competitors > li');
          const keys = ['away', 'home']
          for (const [key, team] of Array.from(teams).map((team, i) => [keys[i], team])) {
            data[key] = {};
            const logo = team.querySelector('img.Logo');
            const url = new URL(logo.src);
            data[key].team = path.basename(url.searchParams.get('img'), '.png');
          }
          data.gameId = makeGameId('nba', Y, M, D, data.away.team, data.home.team);
          data.date = { Y, M, D };
          sportsData.curr['nba'][data.gameId] = data;
        }
      });
    console.log(JSON.stringify(sportsData.curr));
  },
};

const main = () => {
  sportsData.update();
};

main();
