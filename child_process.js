var exec = require('child_process').exec;
var parse = require('./scrape');
var fs = require('fs');

console.log('computer is downloading tax documents');
exec('python download.py 4 1238 61', function(error, stdout, stderr){
  if (error !== null) {
    console.log('exec error: ' + error)
  } else {
    console.log('finished downloading')
    console.log('starting to scrape...')
    scrape_pdfs();
  }
  
})


function scrape_pdfs() {

  var filePaths = fs.readdirSync('data/4-01238-0061');
  
  filePaths.forEach(function(file){
    var path = 'data/4-01238-0061/' + file;
    parse(path, function(tax){ console.log(tax) });
  })

}



