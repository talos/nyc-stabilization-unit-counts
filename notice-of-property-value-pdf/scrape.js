/*jshint node: true*/

var textract = require('textract');
var _ = require('underscore');
var walk = require('walk');
var path = require('path');
var incomeTest1 =
  /(\s*)Gross Income:(\s*)We estimated gross income at \$(.*)\./;
var incomeTest2 = /Estimated Gross Income:(\s*)\$(.*)/;
var expensesTest1 = /(\s*)Expenses:(\s*)We estimated expenses at \$(.*)\./;
var expensesTest2 = /Estimated Expenses:(\s*)\$(.*)/;
var headers = ['bbl', 'date', 'borough', 'block', 'lot',
  'estimatedGrossIncome', 'estimatedExpenses'],
    walkOptions;

function parse (path, chunks) {
  //var docDate, docYear;
  var income, expenses,
      pathSplit = path.split('/'),
      borough = Number(pathSplit[pathSplit.length - 4]),
      block = Number(pathSplit[pathSplit.length - 3]),
      lot = Number(pathSplit[pathSplit.length - 2]),
      bbl = [borough, block, lot].join(''),
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
    borough: borough,
    block: block,
    lot: lot,
    bbl: bbl,
    estimatedGrossIncome: income ? Number(income.replace(/,/g, '')) : '',
    estimatedExpenses: expenses ? Number(expenses.replace(/,/g, '')) : ''
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
          fileStats.name.match(/Notice of Property Value\.pdf/i)) {
        var fullPath = path.join(root, fileStats.name);
        textract('application/pdf', fullPath, {
          preserveLineBreaks:true
        }, function(error, text) {
          if (error) {
            console.error("Could not read '" + fullPath + "': " + error);
          } else {
            console.log(
              _.values(_.pick(parse(fullPath, text.split('\n')), headers))
              .join(','));
            next();
          }
        });
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
