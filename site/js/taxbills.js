/*jshint browser:true*/
/*globals $: false, Handlebars: false, querystring: false*/

(function () {

  var summaryTemplate, graphTemplate, rawDataTemplate, alertTemplate;

  /**
   * Get BBL from borough, street & housenumber
   */
  function getBBL(borough, street, houseNumber) {
    return $.ajax({
      url: 'https://who.owns.nyc/geoclient/address.json?' + $.param({
        borough: borough, street: street, houseNumber: houseNumber
      }),
      dataType: 'json'
    }).then(function (addressData) {
      var data = addressData.address;
      if (data.message || data.message2) {
        return new $.Deferred().reject(data.message || data.message2);
      } else {
        data.borough = data.bblBoroughCode;
        data.block = data.bblTaxBlock;
        data.lot = data.bblTaxLot;
        return data;
      }
    }, function () {
      return 'Sorry, geocoding seems to not be working right now. ' +
          'Please try later.';
    });
  }

  /**
   * Get tax data from BBL
   */
  function getTaxData(data) {
    var borough = data.borough,
        block = data.block,
        lot = data.lot,
        taxUrl = '/' + borough + '/' + block + '/' + lot + '/data.json';
    return $.ajax({
      url: taxUrl,
      dataType: 'json'
    }).then(function (table) {
      return {
        borough: borough,
        block: block,
        lot: lot,
        table: table,
        url: taxUrl
      };
    }, function () {
      return "Sorry, I wasn't able to find tax data for that address (" +
        'BBL ' + borough + block + lot + ').';
    });
  }

  /**
   * Draw the Bootstrap Table with raw tax bill data.
   */
  function showRawData(data) {
    var table = data.table;
    if ($.isArray($('#table').bootstrapTable('getData'))) {
      $('#table').bootstrapTable('load', table);
    } else {
      $('#raw-data').empty().append(rawDataTemplate());
      $('#table').bootstrapTable({
        data: table
      });
      // Add a title
      var $title =$('<h4 />')
        .append($('<a />').text(
          'Tax Data for BBL ' + data.borough + data.block + data.lot).attr({
          'href': data.url,
          'target': '_blank'
        }))
        .addClass('odc-title');
      $('.fixed-table-toolbar').prepend($title);
    }
  }

  /**
   * Show graphs using d3.
   */
  function showGraphs(data) {
    $('#history').empty().append(graphTemplate(data));
  }

  /**
   * Show summary data.
   */
  function showSummary(data) {
    var table = data.table,
        lastActivity = table.select(function (t) {
          return t.activityThrough;
        }).max(),
        propertyTax = table.where(function (t) {
          return t.activityThrough === lastActivity &&
            t.key === 'annual property tax';
        }).first().value,
        lastStabilized = table.orderBy(function (t) {
          return t.activityThrough;
        }).where(function (t) {
          return t.key === 'Housing-Rent Stabilization';
        }).last();
    $('#summary').empty().append(summaryTemplate({
      propertyTax: propertyTax,
      lastActivity: lastActivity,
      lastStabilized: lastStabilized
    }));
  }

  /**
   * Show an error message.
   */
  function showError(errorMsg) {
    var $alert = $(alertTemplate({message: errorMsg}));
    $("#alerts").empty().append($alert);
    setTimeout(function () {
      $alert.alert('close');
    }, 4000);
  }

  /**
   * Main
   */
  $(document).ready(function () {
    $.extend($.fn.bootstrapTable.defaults,
             $.fn.bootstrapTable.locales['en-US']);

    summaryTemplate = Handlebars.compile($('#summaryTemplate').text());
    graphTemplate = Handlebars.compile($('#graphTemplate').text());
    rawDataTemplate = Handlebars.compile($('#rawDataTemplate').text());
    alertTemplate = Handlebars.compile($('#alertTemplate').text());

    var query = querystring.parse(window.location.search.substr(1)),
        $borough = $('#borough'),
        $street = $('#street'),
        $houseNumber = $("#houseNumber");

    if (query.borough) {
      $borough.val(query.borough);
    }
    if (query.street) {
      $street.val(query.street);
    }
    if (query.houseNumber) {
      $houseNumber.val(query.houseNumber);
    }

    $('#bbl-form').submit(function (evt) {
      evt.preventDefault();
      var borough = $borough.val(),
          street = $street.val(),
          houseNumber = $houseNumber.val();
        history.pushState(null, null, window.location.pathname + '?' +
                          $.param({borough: borough,
                                  street: street,
                                  houseNumber: houseNumber }));
      getBBL(borough, street, houseNumber)
        .then(getTaxData)
        .then(function (data) {
          showRawData(data);
          showGraphs(data);
          showSummary(data);
        })
        .fail(showError);
    });

    if (query.houseNumber && query.borough && query.street) {
      $('#bbl-form').submit();
    }
  });
})();
