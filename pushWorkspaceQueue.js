#!/usr/bin/env node

const fs = require('fs');

const queuePath = `${__dirname}/state/ws_queue.json`;
const ws = parseInt(process.argv[2]);
if (ws > 0 && ws < 10) {
  const curr = JSON.parse(fs.readFileSync(queuePath, 'utf-8'));
  if (curr[0] === ws) { process.exit(); }
  const next = [ws, ...curr.slice(0, 5)];
  fs.writeFileSync(queuePath, JSON.stringify(next));
}
