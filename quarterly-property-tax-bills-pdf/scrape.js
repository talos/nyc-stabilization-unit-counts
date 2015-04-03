/*jshint node: true*/

var textract = require('textract');
var _ = require('underscore');

// input: 'filepath' -> callback(object)
var scrape = function (filepath, callback) {
  textract('application/pdf', filepath, function(err, text){
    if (err) {
      console.error(err);
      console.error('error with: ' + filepath);
      callback();
    } else {
      try {
        var taxDoc = parse_pdf(text.split(" "));
        callback(taxDoc);
      } catch (err) {
        console.error(err);
        console.error('error with: ' + filepath);
        callback();
      }
    }
  })
}

function parse_pdf(arr) {

  var taxDoc = {
    activityThrough: null,
    ownerName: '',
    propertyAddress: '',
    bbl: '',
    mailingAddress: '',
    rentStabilized: null,
    units: null,
    annualPropertyTax: null,
    abatements: [],
    billableAssessedValue: null,
    taxRate: null
  }
  parsing(arr);
  annualPropertyTax(arr);
  return cleanUp(taxDoc); 

  function parsing(arr){
    // base case
    if (_.isEmpty(arr)) { return; }
    if (/Activity/i.test(arr[0]) && /through\s*/i.test(arr[1])) {
      taxDoc.activityThrough = arr[2] + " " + arr[3] + " " + arr[4];
      parsing(arr.slice(4));
    } else if (/Owner/.test(arr[0]) && /name:/.test(arr[1])) {
      ownerName(arr);
    } else if (arr[0] === 'Property' && arr[1] === 'address:') {
      propertyAddress(arr);
    } else if (arr[0] === 'Borough,' && arr[1] === 'block' && arr[2] === '&' && arr[3] === 'lot:') {
      if (arr[4] === 'STATEN') {
        taxDoc.bbl = arr[4] + arr[5] + arr[6] + arr[7] + arr[8];
      } else {
        taxDoc.bbl = arr[4] + arr[5] + arr[6] + arr[7];
      }
      parsing(arr.slice(7));
    } else if (arr[0] === 'Mailing' && arr[1] === 'address:') {
      mailingAddress(arr);
    } else if ( (arr[0] === 'Housing-Rent' && arr[1]) === 'Stabilization' || (arr[0] === 'Stabilization' && arr[2] === '$10/apt.') || (arr[0] === 'Rent' && arr[1] === 'Stabilization')) {
      stabilization(arr);
    } else if (/J-51|Mitchell|421a/g.test(arr[0])) {
      taxDoc.abatements.push(arr[0]);
      parsing(arr.slice(1));
    } else if (/\$\d+,?\d*,?\d*/.test(arr[0]) && arr[1] === 'X' && /\d+\.\d+%$/.test(arr[2])) {
      taxDoc.billableAssessedValue = arr[0];
      taxDoc.taxRate = arr[2];
      parsing(arr.slice(3));
    } else { 
       // don't need this word
      parsing(arr.slice(1)) }

  }

  function ownerName(arr) {
    for (var i = 2; i < arr.length; i++) {
        // if over - recurse
        if(/(\d{6,})|Mailing|Quarterly/.test(arr[i])) {
          parsing(arr.slice(i))
          return;
        } else {
          taxDoc.ownerName = taxDoc.ownerName + arr[i] + " ";
        }
    }
  }

  function propertyAddress(arr) {
    for (var i = 2; i < arr.length; i++) {
        if (/Borough,|Property|Activity/.test(arr[i])){
          parsing(arr.slice(i));
          return;
        } else {
          taxDoc.propertyAddress = taxDoc.propertyAddress + arr[i] + " ";
      }
    }
  }

  function mailingAddress(arr) {
    // if property address shows up after mailing address
    if (arr[2] === 'Property') {
      pdfs_are_terrible(arr);
    } else {
      for (var i =2; i < arr.length; i++){
        if (/Statement|Outstanding|\$0.00|Property/.test(arr[i])){
          parsing(arr.slice(i));
          return;
        } else {
          taxDoc.mailingAddress = taxDoc.mailingAddress + arr[i] + " ";
        }
      }
    }
  }

 function pdfs_are_terrible(arr) {
    var the_end = _.findIndex(arr, function(val){
      return (/Outstanding|Statement/g.test(val));
    })
    var text = arr.slice(2,the_end).join(" ");
    var exec = /(?:Property address: )(.*)(?:Borough, block & lot: )(\w+ ?\(\d\), \d+, \d+)(.*)/g.exec(text);
    if (exec) {
      taxDoc.propertyAddress = exec[1];
      taxDoc.bbl = exec[2];
      taxDoc.mailingAddress = exec[3];
       parsing(arr.slice(the_end));
    } else {
      parsing(arr.slice(3))
    }
  }
  
  function stabilization(arr) {
    taxDoc.rentStabilized = true;
    for (var i = 2; i < 20; i++) {
      if (/^\d{1,3}$/.test(arr[i])) {
        taxDoc.units = arr[i];
        parsing(arr.slice(i))
        return;
      }
    }
    parsing(arr.slice(2))
  }


  function annualPropertyTax(arr) {
    var tax_index = _.findLastIndex(arr, function(val){
      return (/\$\d+,?\d*,?\d*\*\*?/.test(val))
    })
    taxDoc.annualPropertyTax = arr[tax_index];
  }

  function make_bbl(bbl) {
    var arr = bbl.split(',');  
    var exec = /\w+ ?\((\d)\)/.exec(arr[0]);
    return (exec) ? (exec[1] + arr[1].trim() + arr[2].trim()) : 'bbl error';
  }

  // input: taxDoc
  // output: cleaned up taxDoc
  function cleanUp(taxDoc) {
    var clean = taxDoc;

    if (!clean.rentStabilized) {
      clean.rentStabilized = false;
      clean.units = 0;
    }

    clean.mailingAddress = clean.mailingAddress.trim();
    clean.ownerName = clean.ownerName.trim();
    clean.bbl = make_bbl(clean.bbl);
    clean.annualPropertyTax = (clean.annualPropertyTax) ? clean.annualPropertyTax.replace("**", '') : null;
    clean.annualPropertyTax = (clean.annualPropertyTax) ? clean.annualPropertyTax.replace("*", '') : null;
    clean.abatements = _.uniq(clean.abatements);
    clean.propertyAddress = clean.propertyAddress.trim();
    clean.propertyAddress = clean.propertyAddress.replace(clean.ownerName, '');
    
    return clean;

  }

// end of parse_pdf  
}

module.exports = scrape; 
