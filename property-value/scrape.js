var pdfText = require('pdf-text');
//var textract = require('textract');
var _ = require('underscore');
 
var pathToPdf = __dirname + "/" + process.argv[2];
 
pdfText(pathToPdf, function(err, chunks) {
    if (err) { console.log(err); }
    //console.log(chunks);
    console.log(to_json(chunks));
});
 
// textract('application/pdf', pathToPdf, {preserveLineBreaks:true}, function( error, text ) {
//   //console.log(text.split('\n'));
//   console.log(to_json(text.split('\n')));
// });

function to_json(chunks) {

  var prop = {};

  
  var doc_date, doc_year;  

  _.each(chunks, function(element, i, list) {
    //this should only happen once
    if (/(?:(?:JAN|FEB)?R?(?:UARY)?|MAR(?:CH)?|APR(?:IL)?|MAY|JUNE?|JULY?|AUG(?:UST)?|OCT(?:OBER)?|(?:SEPT?|NOV|DEC)(?:EMBER)?)\s+\d{1,2}\s*,?\s*\d{4}$/.test(element)) {
      //console.log(element);
      doc_date = new Date(element);
      doc_year = doc_date.getFullYear();
    }
  });

  _.each(chunks, function(element, i, list) {

    switch(doc_year) {
      case 2010:
        if ( /Gross Income:  We estimated gross income at \$(.*)\./.test(element)){
            var grossIncome = /Gross Income:  We estimated gross income at \$(.*)\./.exec(element)[1];
            prop.grossIncome = grossIncome;
        }
        if ( /UNITS:\s/.test(element)){
            prop.typeOfUnits = list[i+1];
        }                
        break;      
      case 2011:
        if ( /Gross Income:  We estimated gross income at \$(.*)\./.test(element)){
            var grossIncome = /Gross Income:  We estimated gross income at \$(.*)\./.exec(element)[1];
            prop.grossIncome = grossIncome;
        }  
        if ( /UNITS:\s/.test(element)){
            prop.typeOfUnits = list[i+1];
        }              
        break;      
      case 2012:
        if ( /Gross Income:  We estimated gross income at \$(.*)\./.test(element)){
            var grossIncome = /Gross Income:  We estimated gross income at \$(.*)\./.exec(element)[1];
            prop.grossIncome = grossIncome;
        }   
        if ( /UNITS:\s/.test(element)){
            prop.typeOfUnits = list[i+1];
        }             
        break;      
      case 2013:
        if ( /Gross Income:  We estimated gross income at \$(.*)\./.test(element)){
            var grossIncome = /Gross Income:  We estimated gross income at \$(.*)\./.exec(element)[1];
            prop.grossIncome = grossIncome;
        } 
        if ( /Number of Units:/.test(element)){
            prop.typeOfUnits = list[i+1];
        }                
        break;      
      case 2014:
        if ( /Gross Income:  We estimated gross income at \$(.*)\./.test(element)){
            var grossIncome = /Gross Income:  We estimated gross income at \$(.*)\./.exec(element)[1];
            prop.grossIncome = grossIncome;
        }      
        break;
      case 2015:
        if ( /Estimated Gross Income:(\s*)\$(.*)/.test(element)){
          var grossIncome = /Estimated Gross Income:(\s*)\$(.*)/.exec(element)[2];
          prop.grossIncome = grossIncome;
        }      
        break;
      default:
        console.log("didn't get a year");
        break;
    };
  });

  return JSON.stringify(prop);
}