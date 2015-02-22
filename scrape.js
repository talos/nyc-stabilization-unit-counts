var pdfText = require('pdf-text')
var _ = require('underscore');
 
var pathToPdf = __dirname + "/" + process.argv[2];
 
pdfText(pathToPdf, function(err, chunks) {
    if (err) { console.log(err); }
    console.log(chunks);
    console.log(to_json(chunks));
})
 
function to_json(chunks) {
  
  var property_address_index;
  var owner_name_index;
  var bbl_index;
  var rent_stab_index;
  var rentStabilized = null;
  var annual_tax_index;
  var abatements = [];
  var activityThrough;

  _.each(chunks, function(element, i, list) {

    if ( /\s*Property address:?\w?/i.test(element) ){
      property_address_index = i;
    } else if ( /\s*Owner name:?\s*/i.test(element) ) {
        owner_name_index = i;
    } else if ( /\s*Borough, block & lot:\s*/i.test(element) ) {
        bbl_index = i;
    } else if ( /\s*Housing-Rent Stabilization\s*/i.test(element) ) {
      rentStabilized = i;
    } else if (  /\s*J-?51\s*/i.test(element) ) {
      abatements.push(element);
    } else if ( /\s*4-?21\s*/.test(element) ) {
      abatements.push(element);
    } else if ( /\s*Annual property tax\w*/i.test(element)) {
      annual_tax_index = i;
    } else if ( /\s*Activity through\s*/.test(element)) {
      activityThrough = chunks[i + 1];
    }
    else {}
  });


  var property = {
    activityThrough: activityThrough,
    ownerName: chunks[owner_name_index + 1],
    bbl: chunks[bbl_index + 1],
    units: (rentStabilized) ? chunks[rentStabilized + 1] : 0,
    stabilized_amount: (rentStabilized) ? chunks[rentStabilized + 3] : 'n/a',
    rentStabilized: (rentStabilized) ? true : false,
    propertyAddress: get_property_address(),
    annualTax: get_annual_tax(),
    abatements: abatements
  }

    return property;

  function get_annual_tax(){
    var tax = chunks[annual_tax_index + 1];
    if (/\s*\$\d+/.test(tax)) {
      return tax;
    } else {
      return tax + chunks[annual_tax_index + 2]
    }
  }

  function get_property_address () {
    var address = '';
    for (var p = (property_address_index + 1); p < bbl_index; p++) {
      address += chunks[p];
      address += ' '
    }
    return address;
  }


}



