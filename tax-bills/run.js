/*jshint node: true*/

var scraper = require('./scrape.js');
var _ = require('underscore');

var lock = false; // poor man's synchronization.  <3 node.
var headers = [
    "activityThrough",
    "ownerName",
    "propertyAddress",
    "bbl",
    "mailingAddress",
    "rentStabilized",
    "units",
    "annualPropertyTax",
    "abatements",
    "billableAssessedValue",
    "taxRate"
];

function callback(taxDoc) {
  console.log(_.values(_.pick(taxDoc, headers)).join(','));
  lock = false;
}

console.log(headers.join(','));

_.each(process.argv, function (path, i) {
  if (i < 2) {
    return;
  }
  var synchronize = setInterval(function () {
    if (lock === true) {
      return;
    } else {
      lock = true;
    }

    scraper(path, callback);
    clearInterval(synchronize);
  }, 10);
});

