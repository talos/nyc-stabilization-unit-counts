var textract = require('textract');
var _ = require('underscore');

main('samplePDFs/sample3.pdf', function(pdf){console.log(pdf)});


function main(filepath, callback) {
  textract('application/pdf', filepath, function(err, text){
    var pdf = text.split(' ');
    var bill = {}
    callback(pdf);
  })
}



function activity_through(pdf) {

  return _.findIndex(pdf, function(val){
    if (/Activity/.test(val)) { return true;}
  });

}

function activity_through2(pdf) {


  return _.findIndex(pdf, function(val){
    return /Activity/.test(val);
  });

}

function activity_through3(pdf) {

  return _.findIndex(pdf, /Activity/.test);

}

module.exports = {

  main: main
}
