/*jshint node: true*/

var scraper = require('./scrape.js');
var walk = require('walk');
var path = require('path');
var _ = require('underscore');
var stringify = require('csv-stringify');

var walkOptions;

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

function makeCallback(next) {
  return function(taxDoc) {
    if (taxDoc) {
      taxDoc.activityThrough = new Date(
        taxDoc.activityThrough).toISOString().split('T')[0];
      taxDoc.annualPropertyTax = taxDoc.annualPropertyTax ? Number(
        taxDoc.annualPropertyTax.replace(/[$,]/g, '')) :
        taxDoc.annualPropertyTax;
      taxDoc.billableAssessedValue = taxDoc.billableAssessedValue ? Number(
        taxDoc.billableAssessedValue.replace(/[$,]/g, '')) :
        taxDoc.billableAssessedValue;
      taxDoc.taxRate = taxDoc.taxRate ?
        Number(taxDoc.taxRate.replace(/[%]/g, '')) :
        taxDoc.taxRate;
      stringify([_.values(_.pick(taxDoc, headers))], {eof: false, rowDelimiter: 'unix'}, function (err, output) {
        console.log(output);
      });
    }
    next();
  };
}

//console.log(headers.join(','));
stringify([headers], {eof: false, rowDelimiter: 'unix'},function (err, output) {
  console.log(output);
});

walkOptions = {
  listeners: {
    names: function (root, nodeNamesArray) {
      nodeNamesArray.sort(function (a, b) {
        if (a > b) { return 1; }
        if (a < b) { return -1; }
        return 0;
      });
    },
    directories: function (root, dirStatsArray, next) {
      next();
    },
    file: function (root, fileStats, next) {
      if (fileStats.type === 'file' &&
          (fileStats.name.match(/Quarterly Property Tax Bill\.pdf/i) ||
           fileStats.name.match(/Quarterly Statement of Account\.pdf/i))) {
        var fullPath = path.join(root, fileStats.name);
        scraper(fullPath, makeCallback(next));
      } else {
        next();
      }
    },
    errors: function (root, nodeStatsArray, next) {
      console.error('walk error');
      next();
    }
  }
};


walk.walk(process.argv[2], walkOptions);
