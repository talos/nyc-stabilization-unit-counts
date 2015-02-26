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
    mailingAddress: ''
  }
  parsing(arr);
  // additional taxDoc formating here
  return taxDoc; 

  function parsing(arr){
    // base case
    if (_.isEmpty(arr)) { return; }

    var word = arr[0];

    if (/Activity/.test(word) && /through\s*/.test(arr[1])) {
      taxDoc.activityThrough = arr[2] + " " + arr[3] + " " + arr[4];
      parsing(arr.slice(4));
    } else if (/Owner/.test(word) && /name:/.test(arr[1])) {
      // look for for end of owner name
      for (var i = 2; i < arr.length; i++) {
        // if over - recurse
        if(/(\d{6,})|Mailing|Quarterly/.test(arr[i])) {
          parsing(arr.slice(i))
          return;
        } else {
          taxDoc.ownerName = taxDoc.ownerName + arr[i] + " ";
        }
      }
    } else if (arr[0] === 'Property' && arr[1] === 'address:') {
      for (var i = 2; i < arr.length; i++) {
        if (/Borough,|Property/.test(arr[i])){
          parsing(arr.slice(i));
          return;
        } else {
          taxDoc.propertyAddress = taxDoc.propertyAddress + arr[i] + " ";
        }
      }
    } else if (arr[0] === 'Borough,' && arr[1] === 'block' && arr[2] === '&' && arr[3] === 'lot:') {
      taxDoc.bbl = arr[4] + arr[5] + arr[6] + arr[7];
      parsing(arr.slice(7));
    } else if (arr[0] === 'Mailing' && arr[1] === 'address:') {

      // case if property address shows up after mailing address

      for (var i =2; i < arr.length; i++){
        if (/Statement|Outstanding|\$0.00/.test(arr[i])){
          parsing(arr.slice(i));
          return;
        } else {
          taxDoc.mailingAddress = taxDoc.mailingAddress + arr[i] + " ";
        }
      }

    }
    // don't need this word
    else { parsing(arr.slice(1)) }

  }


}