var should = require('should');
var parse = require('./scrape')


var result = {
  activityThrough: 'August 22, 2014',
  ownerName: 'PARKER ENG LLC',
  propertyAddress: '2425 STEINWAY ST.',
  bbl: '4006860007',
  mailingAddress: 'PARKER ENG LLC 18422 GRAND CENTRAL PKWY. JAMAICA, NY 11432-5801',
  rentStabilized: true,
  units: '12',
  annualPropertyTax: '$38,804',
  abatements: [],
  taxRate: '13.1450%',
  billableAssessedValue: '$295,200'
}


describe('sample 2', function(){
// this.timeout(15000);
var sample3;
  before(function(done){

    parse('samplePDFs/sample2.pdf', function(pdf){
      sample3 = pdf;
      done();
    })
  });


  it('should prase correctly', function(){
    console.log(sample3)
    sample3.should.eql(result);

  })

})


