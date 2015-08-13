(function () {

  /**
   * Render a tax table based off of BBL
   */
  function renderTable(borough, street, houseNumber) {
    $.ajax({
      url: 'https://who.owns.nyc/geoclient/address.json?borough=' +
             borough + '&street=' + street + '&houseNumber=' + houseNumber,
      dataType: 'json'
    }).done(function (addressData) {
      var borough = addressData.address.bblBoroughCode,
          block = addressData.address.bblTaxBlock,
          lot = addressData.address.bblTaxLot;
      if (borough && block && lot) {
        $.ajax({
          url: '/' + borough + '/' + block + '/' + lot + '/data.json',
          dataType: 'json'
        }).done(function (data) {
          if ($.isArray($('#table').bootstrapTable('getData'))) {
            $('#table').bootstrapTable('load', data);
          } else {
            $('#content').empty().append($('#tableTemplate')
                                         .clone()
                                         .removeClass('template')
                                         .attr('id', 'table'));
            $('#table').bootstrapTable({
              data: data
            });
          }
        }).error(function (err) {
          $('#content').empty().append($('<div />').addClass('error').text(
            "Sorry, I wasn't able to find tax data for that address."
          ));
        });
      } else {
        $('#content').empty().append($('<div />').addClass('error').text(
          "Sorry, I wasn't able to recognize that address: " + addressData.address.message
        ));
      }
    }).error(function (err) {
      $('#content').empty().append($('<div />').addClass('error').text(
        "Sorry, geocoding seems to not be working right now. Please try later."
      ));
    });
  }

  $(document).ready(function () {
    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['en-US']);

    $('#bbl-form').submit(function (evt) {
      evt.preventDefault();
      renderTable($('#borough').val(),
                  $('#street').val(),
                  $('#houseNumber').val());
      //renderTable($('#borough').val(),
      //            $('#block').val(),
      //            $('#lot').val());
    });
  });
})();
