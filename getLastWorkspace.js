#!/usr/bin/env node

const fs = require('fs');

const queuePath = `${__dirname}/state/ws_queue.json`;
const curr = JSON.parse(fs.readFileSync(queuePath, 'utf-8'));
console.log(curr[1] || 1)
