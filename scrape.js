var textract = require('textract');
var _ = require('underscore');

main('samplePDFs/sample6.pdf', function(pdf){console.log(pdf)});


function main(filepath, callback) {
  textract('application/pdf', filepath, function(err, text){
    // var pdf = text.split(' ');
    // var bill = {}
    callback(text);
  })
}

// function activity_through(pdf) {
//   for (i = 0; i < pdf.length; i ++) {
//     if (/Activity/.test(text) && /through/.test(pdf[i+1])) {
//       return pdf[i+2] + pdf[i+3] + pdf[i+3]
    
//   }
// }


// function activity_through(pd) {

//   _.chain(pdf).findIndex(function(val){
//     return /Activity/.test(val);
//   }).tap(function(index){

//     if (/through/.test(pdf[index+1])) {
//       return pdf[i+2] + pdf[i+3] + pdf[i+3];
//     } else {
//       activity_through(pdf.slice(index+1))
//     }

//   }).value();
// }

module.exports = {

  main: main
}

  // _.each(pdf, function(text, i, l){
  //   if (/Activity/.test(text) && /through/.test(pdf[i+1])) {
  //     activity = pdf[i+2] + pdf[i+3] + pdf[i+3]
  //   }
  // })
  // return activity;
