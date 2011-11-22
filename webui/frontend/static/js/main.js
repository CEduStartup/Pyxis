var MINUTE = 60 * 1000;
var HOUR   = MINUTE * 60;
var DAY    = HOUR * 24;

var chart, options;

function default_config(chart_type) {
    return {
          chart: {
             renderTo: 'container',
             defaultSeriesType: chart_type,
             zoomType: 'xy'
          },
          title: {
             text: ''
          },
          xAxis: {
            type: 'datetime'
          },
          yAxis: {
             title: {
                text: ''
             }
          },
          legend: {
          },
          tooltip: {
            formatter: tooltip_formatter
          },
          plotOptions: get_plot_options(chart_type),
          series: []
    }
};

function update_chart() {
    var data = $('#form').serialize();

    $.ajax({
        url: "/trackers/get_data_to_display",
        type: "POST",
        dataType: "json",
        data: data,
        success: function(data, lviv){
            var d = new Date();
            var offset = d.getTimezoneOffset() * 60 * 1000;
            for(var i=0; i<data.length; i++){
              data[i].pointStart *= 1000;
              data[i].pointStart -= offset;
              data[i].pointInterval *= 1000;
              for(var j=0; j<data[i].data.length; j++){
                data[i].data[j][0] *= 1000;
                data[i].data[j][0] -= offset;
              }
            }
            var chart_type = $('#id_types').val();
            var config = default_config(chart_type);
            config.series = data;
            render_chart(config, chart_type);
            options = config;
        },
    });
}

function render_chart(config, type) {
    config = config || options;
    type = type || 'line';
    config.plotOptions = get_plot_options(type);
    config.chart.defaultSeriesType = type;
    chart = new Highcharts.Chart(config);
}

function get_plot_options(chart_type){
  if(chart_type == 'line' || chart_type == 'area') {
    return {
      series: {
        marker: {
          enabled: false,
          states: {
            hover: {
              enabled: true,
              radius: 4
            }
          }
        }
      }
    }
  } else {
    return {
      column: {
        pointPadding: 0.2,
        borderWidth: 0
      }
    }
  }
}

function tooltip_formatter(){
  var period = $('#id_periods').val();
  var text = '<b>' + this.series.name + ': ' + this.y + '</b><br/>';
  if(period == 'minute'){
    return text + 'Data for ' + Highcharts.dateFormat('%e %b %H:%M', this.x);
  }
  if(period == '5minutes' || period == '15minutes'){
    var n = {'5minutes': 5, '15minutes': 15}[period];
    return text + 'Data for ' + Highcharts.dateFormat('%e %b %H:%M', this.x) +
        ' - ' + Highcharts.dateFormat('%H:%M', this.x + MINUTE * n);
  }
  if(period == 'hour'){
    return text + 'Data for ' + Highcharts.dateFormat('%e %b %H:%M', this.x) +
        ' - ' + Highcharts.dateFormat('%H:%M', this.x + HOUR - MINUTE);
  }
  if(period == 'day'){
    return text + 'Data for ' + Highcharts.dateFormat('%e %b %y', this.x);
  }
  if(period == 'week'){
    return text + Highcharts.dateFormat('%a %e %b', this.x) +
        ' - ' + Highcharts.dateFormat('%a %e %b %y', this.x + DAY * 7 - MINUTE);
  }
  if(period == 'month'){
    return text + Highcharts.dateFormat('%B %Y', this.x);
  }
  return text += 'Data for ' + Highcharts.dateFormat('%Y', this.x);
}

function alert_message(data, success_message, error_message) {
    var success_message = success_message || 'View has been saved!'
    var error_message = error_message || 'Somthing wrong'

    var alert_message = $('#alert-message');
    console.log(data);
    if (data.success) {
        alert_message.removeClass('error');
        alert_message.addClass('success');
        alert_message.html(success_message);
    }
    else {
        alert_message.removeClass('success');
        alert_message.addClass('error');
        alert_message.html(error_message);
    }
    alert_message.fadeIn(300).delay(3000).fadeOut(500);
}
