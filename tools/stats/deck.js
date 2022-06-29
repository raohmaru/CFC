const fs = require('fs');
const libxmljs = require('libxmljs');

const QTY = [0, ',', '.', ':'];
const HAND_SIZE = 5;

if (!process.argv[2]) {
    console.log('Missing raw deck string.');
    process.exit(1);
}
const exportFile = process.argv[3];
// const rawDeck = '4o:bp:2a.g:81:3o:5l:a:bq,7l:1k:7b,13:bn.ba:a4:2i:80.1c,3r.';
const rawDeck = process.argv[2];

const setRaw = fs.readFileSync('../../o8g/Sets/aa867ea1-89f8-4154-8e20-2263eddb8354/set.xml', 'utf8');
const setXml = libxmljs.parseXml(setRaw);
const cardsGIDs = setXml.get('//property[@name="Gid"]');

let deckLen = 0;
let spCost = 0;
let spProd = 0;
let deadHand = 0;
let deadHandProb = 0;
let deckXML = '';
const types = {
    Character: 0,
    Action: 0,
    Reaction: 0
};

rawDeck.match(/\w+\W/g).map(m => {
    const gid = parseInt(m.substring(0, m.length - 1), 32);
    const card = cardsGIDs.get(`//property[@value="${gid}"]/parent::node()`);
    const qty = parseInt(QTY.indexOf(m.at(-1)), 10);
    const sp = parseInt(card.get('property[@name="SP"]').attr("value").value(), 10);
    const type = card.get('property[@name="Type"]').attr("value").value();
    const name = card.attr('name').value();
    deckLen += qty;
    types[type] += qty;
    if (sp >= 0) {
        spProd += sp;
    } else {
        spCost += sp;
        deadHand += qty;
    }
    console.log(`x${qty}  ${name}`);
    if (exportFile) {
        deckXML += `    <card qty="${qty}" id="${card.attr('id').value()}">${name}</card>\n`;
    }
});
console.log('————————————————');
console.log(`${deckLen} cards (${Object.entries(types).map(e => `${e[1]} ${e[0].toLowerCase()}s`).join(', ')})`);
console.log(`SP production: ${spProd}`);
console.log(`SP cost: ${spCost}`);

if (deadHand >= HAND_SIZE) {
    deadHandProb = 1;
    for (let i = 0; i < HAND_SIZE; i++) {
        deadHandProb *= deadHand / deckLen;
        deadHand--;
        deckLen--;
    }
}
console.log(`Dead starting hand chance: ${(deadHandProb * 100).toFixed(3)}%`);

if (exportFile) {
    fs.writeFileSync(exportFile, `<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<deck game="e3d56d9e-900d-49c6-b6ae-22cbb51be153">
  <section name="Main" shared="False">
    ${deckXML.trim()}
  </section>
  <notes><![CDATA[]]></notes>
</deck>`);
    console.log('OCTGN deck file created');
}