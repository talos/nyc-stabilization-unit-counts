var textract = require('textract');
var _ = require('underscore');
 
var pathToPdf = __dirname + "/" + process.argv[2];
 
textract('application/pdf', pathToPdf, {preserveLineBreaks:true}, function( error, text ) {
  console.log(to_json(text.split('\n')));
});

function to_json(chunks) {

  var prop = {
    estimatedGrossIncome: '',
    estimatedExpenses: ''
  };

  var doc_date, doc_year;  

  _.each(chunks, function(element, i, list) {

    if ( /(\s*)Gross Income:(\s*)We estimated gross income at \$(.*)\./.test(element)){
        var grossIncome = /(\s*)Gross Income:(\s*)We estimated gross income at \$(.*)\./.exec(element)[3];
        prop.estimatedGrossIncome = grossIncome;
    }
    else if ( /Estimated Gross Income:(\s*)\$(.*)/.test(element)){
      var grossIncome = /Estimated Gross Income:(\s*)\$(.*)/.exec(element)[2];
      prop.estimatedGrossIncome = grossIncome;
    }   

    if ( /(\s*)Expenses:(\s*)We estimated expenses at \$(.*)\./.test(element)){
        var expenses = /(\s*)Expenses:(\s*)We estimated expenses at \$(.*)\./.exec(element)[3];
        prop.estimatedExpenses = expenses;
    } 
    else if ( /Estimated Expenses:(\s*)\$(.*)/.test(element)){
      var expenses = /Estimated Expenses:(\s*)\$(.*)/.exec(element)[2];
      prop.estimatedExpenses = expenses;
    }       

  });

  return JSON.stringify(prop);
}