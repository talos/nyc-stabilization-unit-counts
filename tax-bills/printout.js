var fs = require('fs');
var textract = require('textract');
var scrape  = require('./scrape');

fs.readdir(process.argv[2], function(err, files){
  if (err) {console.log('error: ' + err) }
  files.forEach(function(file){
    var filePath = process.argv[2] + '/' + file;
    scrape(filePath, function(taxDoc) {
      console.log(taxDoc);
    })
    // raw_text(filePath);
  })
})


function raw_text(filepath) {
  textract('application/pdf', filepath, function(err, text){
    console.log(text);
  })
}
