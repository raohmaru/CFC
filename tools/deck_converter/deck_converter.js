var fs = require('fs');

var rawdecks = fs.readFileSync('raw_decks.txt', 'utf8'),
	cardlist = fs.readFileSync('cards_list.txt', 'utf8').split('\n'),
	cardsuuid = fs.readFileSync('cards_uuid.txt', 'utf8').split('\n'),
	count = 0,
	deck_found = 0,
	deck = '',
	offset = 0x000625A0,
	card, num, name, orig_name, uuid, qty;

for(var i=0; i<rawdecks.length; i+=4) {
	if(count === 0) {
		deck += '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
<deck game="e3d56d9e-900d-49c6-b6ae-22cbb51be153" sleeveid="0">\n\
  <section name="Main" shared="False">';
		// console.log('----------------------------------------------- Deck #' + (deck_found+1) + ' @0x000' + offset.toString(16));
	}
	card = rawdecks.substr(i, 4);
	num = card[3] + card.substr(0, 2);
	num = parseInt(num, 16);
	qty = parseInt(card[2], 10);
	uuid = cardsuuid[num-1].substr(0, 36);
	name = cardsuuid[num-1].substr(38).trim();
	orig_name = cardlist[num-1].substr(0, 16).trim();
	deck += '\n    <card qty="'+qty+'" id="'+uuid+'">'+name+'</card>';
	// console.log(card + ': #' + padleft(num) + ' ' + orig_name + ' (' + qty + ')');
	count += qty;
	offset += 2;
	if(count === 50) {
		deck += '\n  </section>\n\
  <notes><![CDATA[]]></notes>\n\
</deck>';
		count = 0;
		deck_found++;
		fs.writeFileSync("deck_"+deck_found+".o8d", deck);
		deck = '';
	}
}

console.log('Found ' + deck_found + ' decks');

function padleft(str) {
	str = String(str);
	return ('000'+str).substring(str.length);
}