function parse_pdf(text) {

  var pdf = text.split(' ');
  var property = {}
  parsing(pdf);
  // additional property formating here
  return property; 
  
  function parsing(arr){
    // base case
    if (arr == []) {
      return;
    }

    var word = pdf[0];

    if (/Activty/.test(word)) {
      // do something with it
      property.activityThrough = pdf[1] + pdf[2] + pdf[3];
      parser(arr.slice(1));
    } else if ( another-case) {
      // do something with it
    } else {
      // don't need this word
      parser(arr.slice(1))
    }

  }


}