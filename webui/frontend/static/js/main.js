var chart;

function build_chart(data, chart_type) {
   options = {
          chart: {
             renderTo: 'container',
             defaultSeriesType: chart_type,
          },
          title: {
             text: 'Monthly Average Rainfall'
          },
          subtitle: {
             text: 'Source: WorldClimate.com'
          },
          xAxis: {
             categories: [
                'Jan',
                'Feb',
                'Mar',
                'Apr',
                'May',
                'Jun',
                'Jul',
                'Aug',
                'Sep',
                'Oct',
                'Nov',
                'Dec'
             ]
          },
          yAxis: {
             min: 0,
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
                return ''+
                   this.x +': '+ this.y +' mm';
             }
          },
          plotOptions: {
             column: {
                pointPadding: 0.2,
                borderWidth: 0
             }
          },
          series: [{
             name: 'Tokyo',
             data: data,
          }],
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
    config.chart.defaultSeriesType = type;
    chart = new Highcharts.Chart(config);
    console.log(chart);
}

