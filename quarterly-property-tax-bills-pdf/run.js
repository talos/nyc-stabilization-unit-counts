/*jshint node: true*/

var scraper = require('./scrape.js');
var walk = require('walk');
var path = require('path');
var _ = require('underscore');
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
      _.each(taxDoc, function (v, k) {
        if (typeof v === 'string') {
          if (v.search(',') !== -1) {
            v = v.replace(/'"'/g, '\\"');
            taxDoc[k] = '"' + v + '"';
          }
        }
      });
      console.log(_.values(_.pick(taxDoc, headers)).join(','));
    }
    next();
  };
}

console.log(headers.join(','));

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
          fileStats.name.match(/Quarterly Property Tax Bill\.pdf/i)) {
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
