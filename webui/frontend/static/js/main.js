var chart;

function build_chart(data, chart_type) {
   options = {
          chart: {
             renderTo: 'container',
             defaultSeriesType: chart_type,
             zoomType: 'x'
          },
          title: {
             text: 'Monthly Average Rainfall'
          },
          subtitle: {
             text: 'Source: WorldClimate.com'
          },
          xAxis: {
            type: 'datetime'
            //categories: x_cats
          },
          yAxis: {
             title: {
                text: 'Rainfall (mm)'
             }
          },
          legend: {
             layout: 'vertical',
             align: 'left',
             verticalAlign: 'top',
             x: 70,
             y: 0,
             floating: true,
             shadow: true
          },
          tooltip: {
            formatter: function() {
              console.log(this);
              return '<b>'+ this.series.name +'</b><br/>'+
                     '"<b>' +Highcharts.dateFormat('%e %b %H:%M', this.x) +'</b>" '+ this.y;
            }
          },
          plotOptions: get_plot_options(chart_type),
          series: data
        }

    chart = new Highcharts.Chart(options);
};

function update_chart() {
    var values = {};
    $.each($('#form').serializeArray(), function(i, field) {
        values[field.name] = field.value;
    });

    $.ajax({
        url: "/trackers/call",
        type: "POST",
        dataType: "json",
        data: values,
        success: function(data, lviv){
            var tracker = {
                'name': 'Lviv',
                'data': data,
            }
            options.series.push(tracker);
            render_chart(options);
        },
    });
}

function render_chart(config, type) {
    config = config || options
    type = type || 'line';
    config.plotOptions = get_plot_options(type);
    config.chart.defaultSeriesType = type;
    chart = new Highcharts.Chart(config);
    console.log(chart);
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
