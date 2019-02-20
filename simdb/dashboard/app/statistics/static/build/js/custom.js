
function init_chart_entry_types(){

    if( typeof (echarts) === 'undefined'){ return; }

    // init echart
    var echartPie = echarts.init(document.getElementById('echart_entry_types'));

    // get data via post method
    // URL must have a leading and trailing slash
    $.post('/statistics/entry_types/'
    ).done(function(response) {

        // specify chart configuration item and data
        var option = {
          title : {
              text: 'Type',
              x:'center'
          },
          tooltip : {
              trigger: 'item',
              formatter: "{a} <br/>{b} : {c} ({d}%)"
          },
          series : [
              {
                  name: 'Entry type',
                  type: 'pie',
                  radius : '55%',
                  center: ['50%', '60%'],
                  data: response["data"],
                  itemStyle: {
                      emphasis: {
                          shadowBlur: 10,
                          shadowOffsetX: 0,
                          shadowColor: 'rgba(0, 0, 0, 0.5)'
                      }
                  }
              }
          ]
        };

        // use configuration item and data specified to show chart
        echartPie.setOption(option);


    }).fail(function() {
        window.alert("fail");
    });


};


function init_chart_entry_owner(){

    if( typeof (echarts) === 'undefined'){ return; }

    // init echart
    var echartPie = echarts.init(document.getElementById('echart_entry_owner'));

    // get data via post method
    // URL must have a leading and trailing slash
    $.post('/statistics/entry_owner/'
    ).done(function(response) {

        // specify chart configuration item and data
        var option = {
          title : {
              text: 'Owner',
              x:'center'
          },
          tooltip : {
              trigger: 'item',
              formatter: "{a} <br/>{b} : {c} ({d}%)"
          },
          series : [
              {
                  name: 'Entry owner',
                  type: 'pie',
                  radius : '55%',
                  center: ['50%', '60%'],
                  data: response["data"],
                  itemStyle: {
                      emphasis: {
                          shadowBlur: 10,
                          shadowOffsetX: 0,
                          shadowColor: 'rgba(0, 0, 0, 0.5)'
                      }
                  }
              }
          ]
        };

        // use configuration item and data specified to show chart
        echartPie.setOption(option);


    }).fail(function() {
        window.alert("fail");
    });


};

$(document).ready(function() {

    init_chart_entry_types();
    init_chart_entry_owner();

});