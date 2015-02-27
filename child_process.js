var exec = require('child_process').exec;

exec('python download.py 1 1576 5', function(error, stdout, stderr){
  if (error !== null) {
    console.log('exec error: ' + error)
  }

  console.log('finished downloading')

})