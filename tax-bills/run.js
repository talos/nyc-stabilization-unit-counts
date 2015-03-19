/*jshint node: true*/

var scraper = require('./scrape.js');
var _ = require('underscore');

var lock = false; // poor man's synchronization.  <3 node.
var headers = [
    "bbl",
    "activityThrough",
    "rentStabilized",
    "units",
    "ownerName",
    "propertyAddress",
    "mailingAddress",
    "annualPropertyTax",
    "abatements",
    "billableAssessedValue",
    "taxRate"
];

function callback(taxDoc) {
  taxDoc.activityThrough = new Date(
    taxDoc.activityThrough).toISOString().split('T')[0];
  taxDoc.annualPropertyTax = Number(
    taxDoc.annualPropertyTax.replace(/[$,]/g, ''));
  taxDoc.billableAssessedValue = Number(
    taxDoc.billableAssessedValue.replace(/[$,]/g, ''));
  taxDoc.taxRate = Number(taxDoc.taxRate.replace(/[%]/g, ''));
  _.each(taxDoc, function (v, k) {
    if (typeof v === 'string') {
      if (v.search(',') !== -1) {
        v = v.replace(/'"'/g, '\\"');
        taxDoc[k] = '"' + v + '"';
      }
    }
  });
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

