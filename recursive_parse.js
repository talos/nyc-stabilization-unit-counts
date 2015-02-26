function parse_pdf(text) {

  var pdf = text.split(' ');
  var taxDoc = {}
  parsing(pdf);
  // additional taxDoc formating here
  return taxDoc; 
  
  function parsing(arr){
    // base case
    if (arr == []) {
      return;
    }

    var word = arr[0];

    if (/Activty/.test(word) && /through\s*/.test(arr[1])) {
      taxDoc.activityThrough = arr[2] + arr[3] + arr[4];
      parser(arr.slice(4));
    } else if (/Owner/.test(word) && /name:/.test(arr[1])) {

       
            if (/(\d{6,})|Mailing|Quarterly/.test(arr[2]) {
        // end of word
        taxDoc.ownerName = ownerName + arr[2]

      }
      if(arr[2])

      if (arr[2])
      // 
      Owner name: [large number, Mailing, Quarterly, 
      // do something with it
    } else {
      // don't need this word
      parser(arr.slice(1))
    }

  }


}