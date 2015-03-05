var exec = require('child_process').exec;
var fs = require('fs');
var async = require('async');

var bbls = [] // array of bbls
var error_bbls = []; // hold errors

var bbls = fs.readFileSync('3441.txt').toString().split('\n');
// make queue
var q = async.queue(function (task, callback){
  download_pdfs(task.bbl, callback);
}, 2);

// fill queue
bbls.forEach(function(bbl){
  q.push({'bbl': bbl});
})

// when done write error file
q.drain = function() {
  if(error_bbls.length) {
     fs.writeFile('bblerrors.csv', error_bbls.join(','), function(err){
        if (err) {
          console.log('error-file-writing-error' + err);
        } else {
          console.log('all done')
        }
     })
   }  else {
    console.log('no errors!');
    console.log('complete');
   }
}

// input string, callback -> 
// downloads pdfs 
function download_pdfs(bbl, done){
  var bbl_array = bbl.split('');
  var bor = bbl_array[0];
  var block = bbl_array.slice(1,6).join('');
  var lot = bbl_array.slice(6,10).join('');
  var command = 'python download.py' + ' ' + bor + ' ' + block + ' ' + lot;

  exec(command, function(error, stdout, stderr){
    if (error) { 
      console.log('bbl error'); 
      error_bbls.push(bbl);
    }
    done();
  })

}



