var should = require('should');
var pdf = require('./scrape')


var result = {
  activityThrough: 'August 22, 2014',
  ownerName: 'PARKER ENG LLC',
  propertyAdd: '2425 STEINWAY ST.',
  bbl: '4006860007',
  mailingAddress: 'PARKER ENG LLC\n18422 GRAND CENTRAL PKWY\nJAMAICA, NY 11432-5801',
  rentStabilized: true,
  units: '12',
  annualPropertyTax: '$38,804',
  abatements: [],
  taxRate: '13.1450%'
}


describe('sample 3', function(){
// this.timeout(15000);
var sample3;
  before(function(done){

    pdf.main('samplePDFs/sample3.pdf', function(pdf){
      sample3 = pdf;
      done();
    })
  });


  it('should prase correctly', function(){
    console.log(sample3)
    sample3.should.eql(result);

  })

})


