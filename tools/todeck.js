var fs = require('fs'),
	util = require('util'),
	parseString = require('xml2js').parseString;
file = 'set.xml'
xml = fs.readFileSync(file, 'utf8');

parseString(xml, function (err, result) {
	result.set.cards[0].card.forEach(function(card){
		var props = mapProperties(card.property);
		if(props.Type === 'Character' && props.Rules)
			console.log(util.format('<card qty="1" id="%s">%s</card>', card.$.id, card.$.name));
	});
});

function mapProperties(arr) {
	var obj = {};
	arr.forEach(function(prop){
		obj[prop.$.name] = prop.$.value;
	})
	return obj;
}