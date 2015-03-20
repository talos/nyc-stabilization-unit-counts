/*jshint node: true*/

var textract = require('textract');
var _ = require('underscore');
var incomeTest1 =
  /(\s*)Gross Income:(\s*)We estimated gross income at \$(.*)\./;
var incomeTest2 = /Estimated Gross Income:(\s*)\$(.*)/;
var expensesTest1 = /(\s*)Expenses:(\s*)We estimated expenses at \$(.*)\./;
var expensesTest2 = /Estimated Expenses:(\s*)\$(.*)/;
var headers = ['bbl', 'date', 'borough', 'block', 'lot',
  'estimatedGrossIncome', 'estimatedExpenses'];
var lock = false; // poor man's synchronization.  <3 node.

function parse (path, chunks) {
  //var docDate, docYear;
  var income, expenses,
      pathSplit = path.split('/'),
      bbl = pathSplit[pathSplit.length - 2].split('-'),
      nameComponents = pathSplit[pathSplit.length - 1].split(' - '),
      date = new Date(nameComponents[0]).toISOString().split('T')[0];

  _.each(chunks, function(element) {
    if (incomeTest1.test(element)) {
      income = incomeTest1.exec(element)[3];
    } else if (incomeTest2.test(element)) {
      income = incomeTest2.exec(element)[2];
    }

    if (expensesTest1.test(element)){
      expenses = expensesTest1.exec(element)[3];
    } else if (expensesTest2.test(element)) {
      expenses = expensesTest2.exec(element)[2];
    }
  });

  return {
    date: date,
    borough: Number(bbl[0]),
    block: Number(bbl[1]),
    lot: Number(bbl[2]),
    bbl: Number(bbl.join('')),
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

  var synchronize = setInterval(function () {
    if (lock === true) {
      return;
    } else {
      lock = true;
    }
    textract('application/pdf', absPath, {
      preserveLineBreaks:true
    }, function(error, text) {
      if (error) {
        console.error("Could not read '" + absPath + "': " + error);
      } else {
        console.log(
          _.values(_.pick(parse(path, text.split('\n')), headers)).join(','));
      }
      lock = false;
    });
    clearInterval(synchronize);
  }, 10);
});

