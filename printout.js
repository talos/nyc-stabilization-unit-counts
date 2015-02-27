var textract = require('textract');
var _ = require('underscore');

main('samplePDFs/sample' + process.argv[2] + '.pdf');

function main(filepath, callback) {
  textract('application/pdf', filepath, function(err, text){
    console.log(text.split(' '))
    // console.log(text);
  })
}
