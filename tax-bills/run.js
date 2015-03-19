/*jshint node: true*/

var scraper = require('./scrape.js');

function callback(taxDoc) {
  console.log(taxDoc);
}

scraper(process.argv[2], callback);
