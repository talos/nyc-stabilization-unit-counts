var textract = require('textract');
var _ = require('underscore');

main('samplePDFs/sample1.pdf');
main('samplePDFs/sample2.pdf');
main('samplePDFs/sample3.pdf');
main('samplePDFs/sample4.pdf');
main('samplePDFs/sample5.pdf');
main('samplePDFs/sample6.pdf');
main('samplePDFs/sample7.pdf');
main('samplePDFs/sample8.pdf');
main('samplePDFs/sample9.pdf');
main('samplePDFs/sample10.pdf');

function main(filepath) {
  textract('application/pdf', filepath, function(err, text){

    var taxDoc = parse_pdf(text.split(" "));
    console.log(taxDoc);
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
  // additional taxDoc formating here
  annualPropertyTax(arr);
  return cleanUp(taxDoc); 

  function parsing(arr){
    // base case
    if (_.isEmpty(arr)) { return; }

    var word = arr[0];

    if (/Activity/.test(word) && /through\s*/.test(arr[1])) {
      taxDoc.activityThrough = arr[2] + " " + arr[3] + " " + arr[4];
      parsing(arr.slice(4));
    } else if (/Owner/.test(word) && /name:/.test(arr[1])) {
      // look for for end of owner name
      ownerName(arr);
    } else if (arr[0] === 'Property' && arr[1] === 'address:') {
      propertyAddress(arr);
    } else if (arr[0] === 'Borough,' && arr[1] === 'block' && arr[2] === '&' && arr[3] === 'lot:') {
      taxDoc.bbl = arr[4] + arr[5] + arr[6] + arr[7];
      parsing(arr.slice(7));
    } else if (arr[0] === 'Mailing' && arr[1] === 'address:') {
      // case if property address shows up after mailing address
      mailingAddress(arr);
    } else if (arr[0] === 'Housing-Rent' && arr[1] === 'Stabilization') {
      stabilization(arr);
    } else if (/J-51|Mitchell|421a/g.test(arr[0])) {
      taxDoc.abatements.push(arr[0]);
      parsing(arr.slice(1));
    } else if (/^\$\d+,?\d+/.test(arr[0]) && arr[1] === 'X' && /\d+\.\d+%$/.test(arr[2])) {
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
        if (/Borough,|Property/.test(arr[i])){
          parsing(arr.slice(i));
          return;
        } else {
          taxDoc.propertyAddress = taxDoc.propertyAddress + arr[i] + " ";
      }
    }
  }

  function mailingAddress(arr) {
    for (var i =2; i < arr.length; i++){
      if (/Statement|Outstanding|\$0.00/.test(arr[i])){
        parsing(arr.slice(i));
        return;
      } else {
        taxDoc.mailingAddress = taxDoc.mailingAddress + arr[i] + " ";
      }
    }
  }

  function stabilization(arr) {
    taxDoc.rentStabilized = true;
    if (/\d{1,4}/.test(arr[2])) {
      taxDoc.units = arr[2];
      parsing(arr.slice(2))
    } else if (/\d{1,4}/.test(arr[7])) {
      taxDoc.units = arr[7];
      parsing(arr.slice(7));
    } else {
      for (var i = 7; i < arr.length; i++) {
        if (arr[i] === 'remaining') {
          taxDoc.units = arr[i+1];
          parsing(arr.slice(i));
          break;
        }
      }
    }
  }

  function abatements(arr) {

  }

  function annualPropertyTax(arr) {
    var tax_index = _.findLastIndex(arr, function(val){
      return (/\$\d+,?\d*\*\*/.test(val))
    })
    taxDoc.annualPropertyTax = arr[tax_index];
  }

  // input: taxDoc
  // output: cleaned up taxDoc
  function cleanUp(taxDoc) {
    var clean = taxDoc;

    if (!clean.rentStabilized) {
      clean.rentStabilized = false;
      clean.units = 0;
    }

    clean.abatements = _.uniq(clean.abatements);
    
    return clean;

  }

// end of parse_pdf  
}