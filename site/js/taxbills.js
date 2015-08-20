/*jshint browser:true, camelcase: false*/
/*globals $: false, Handlebars: false, querystring: false, google: false*/

(function () {

  var summaryTemplate, graphTemplate, rawDataTemplate, alertTemplate;

  /**
   * Get BBL from borough, street & housenumber
   */
  function getBBL(data) {
    return $.ajax({
      url: 'https://who.owns.nyc/geoclient/address.json?' + $.param({
        borough: data.borough, street: data.street, houseNumber: data.houseNumber
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
   * Convert a county to an NYC borough.  Returns undefined if no borough
   * matches.
   */
  function county2borough(county) {
    if (county.match(/^new york/i)) {
      return 1;
    } else if (county.match(/^bronx/i)) {
      return 2;
    } else if (county.match(/^kings/i)) {
      return 3;
    } else if (county.match(/^queens/i)) {
      return 4;
    } else if (county.match(/^richmond/i)) {
      return 5;
    }
  }

  /**
   * Parse google's location output for street number, street name, and
   * borough.
   */
  function parseGoogle(place) {
    var $dfd = new $.Deferred();

    if (!place.address_components) {
      return $dfd.reject("Sorry, I can't work with that address");
    }
    if (!place.address_components[0].types.contains('street_number')) {
      return $dfd.reject("Double-check this address, I can't find it");
    }
    var houseNumber = place.address_components[0].short_name,
        street = place.address_components[1].short_name,
        borough;

    for (var i = 0; i < place.address_components.length; i += 1) {
      var county = place.address_components[i].long_name;
      if (county.match(/county$/i)) {
        borough = county2borough(county);
      }
      if (borough) {
        break;
      }
    }

    if (!borough) {
      return $dfd.reject("Unknown borough");
    }

    $dfd.resolve({
      houseNumber: houseNumber,
      street: street,
      borough: borough
    });
    return $dfd.promise();
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
        //$borough = $('#borough'),
        //$street = $('#street'),
        //$houseNumber = $("#houseNumber");

        /*
    if (query.borough) {
      $borough.val(query.borough);
    }
    if (query.street) {
      $street.val(query.street);
    }
    if (query.houseNumber) {
      $houseNumber.val(query.houseNumber);
    }
   */

  $(document).ready(function () {
    $.extend($.fn.bootstrapTable.defaults,
             $.fn.bootstrapTable.locales['en-US']);

    summaryTemplate = Handlebars.compile($('#summaryTemplate').text());
    graphTemplate = Handlebars.compile($('#graphTemplate').text());
    rawDataTemplate = Handlebars.compile($('#rawDataTemplate').text());
    alertTemplate = Handlebars.compile($('#alertTemplate').text());

    //var query = querystring.parse(window.location.search.substr(1));

    $('#bbl-form').on('submit', function (evt) {
      evt.preventDefault();
    });

    var autocomplete = new google.maps.places.Autocomplete($('#location')[0]);
    autocomplete.setTypes(['address']);
    autocomplete.setBounds(new google.maps.LatLngBounds(
      new google.maps.LatLng(40.49,-74.27),
      new google.maps.LatLng(40.87,-73.68)
    ));
    autocomplete.addListener('place_changed', function() {
      var place = autocomplete.getPlace();


        //history.pushState(null, null, window.location.pathname + '?' +
        //                  $.param({borough: borough,
        //                          street: street,
        //                          houseNumber: houseNumber }));
      parseGoogle(place)
        .then(getBBL)
        .then(getTaxData)
        .then(function (data) {
          showRawData(data);
          showGraphs(data);
          showSummary(data);
        })
        .fail(showError);
    });

    //if (query.houseNumber && query.borough && query.street) {
    //  $('#bbl-form').submit();
    //}
  });
})();
