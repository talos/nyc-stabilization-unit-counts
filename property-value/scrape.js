/*jshint node: true*/
/*globals require*/

var textract = require('textract');
var _ = require('underscore');
var incomeTest1 =
  /(\s*)Gross Income:(\s*)We estimated gross income at \$(.*)\./;
var incomeTest2 = /Estimated Gross Income:(\s*)\$(.*)/;
var expensesTest1 = /(\s*)Expenses:(\s*)We estimated expenses at \$(.*)\./;
var expensesTest2 = /Estimated Expenses:(\s*)\$(.*)/;
var headers = ['estimatedGrossIncome', 'estimatedExpenses'];

function parse (chunks) {

  //var docDate, docYear;
  var income, expenses;

  _.each(chunks, function(element) {
    if (incomeTest1.test(element)) {
      income = incomeTest1.exec(element)[3];
    } else if (incomeTest2.test(element)){
      income = incomeTest2.exec(element)[2];
    }

    if (expensesTest1.test(element)){
      expenses = expensesTest1.exec(element)[3];
    }
    else if (expensesTest2.test(element)){
      expenses = expensesTest2.exec(element)[2];
    }
  });

  return {
    estimatedGrossIncome: income ? Number(income.replace(/,/g, '')) : '',
    estimatedExpenses: expenses ? Number(expenses.replace(/,/g, '')) : ''
  };
}

console.log(headers.join(','));

_.each(process.argv, function (path, i) {
  if (i < 2) {
    return;
  }
  var absPath = __dirname + "/" + path;

  textract('application/pdf', absPath, {
    preserveLineBreaks:true
  }, function( error, text ) {
    if (error) {
      console.error("Could not read '" + absPath + "': " + error);
    } else {
      console.log(_.values(_.pick(parse(text.split('\n')), headers)).join(','));
    }
  });
});
