var fs = require('fs');

var cardlist = fs.readFileSync('cards_list.txt', 'utf8').split('\n'),
	setxml = fs.readFileSync('set.xml', 'utf8'),
	len = cardlist.length - 1,
	count = 0,
	search, idx, name;
	
for(var i=0; i<len; i++) {
	name = cardlist[i].substr(0, 16).trim();
	name = name.replace("'", '&apos;');
	if(i > 320) {  // Start of AC cards
		name = name[0] + name.substr(1).toLowerCase();
	}
	search = '<card name="' + name + '" id="';
	idx = setxml.indexOf(search);
	if(idx > -1) {
		// console.log(name);
		console.log(setxml.substr(idx+search.length, 36) + "    " + name);
		count++;
	} else {
		console.log(name);
	}
}

console.log(count + ' matches out of ' + len);