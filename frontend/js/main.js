"use strict";


apiServices.fetchPowerConsumption().then( response => {

    let trace = {
        x: response.datetime.map( 
            (val, idx, arr) => {return new Date(val)}),
        y: response.power_kW,
        type: "scatter"
    };

    let _today = new Date()
    let _yesterday = new Date()
    _yesterday.setDate(_today.getDate() - 1)

    let layout = {
        xaxis: {
            range: [_yesterday, _today],
            type: 'date'
        }
    }

    Plotly.newPlot("stromverbrauch-line-chart", [trace], layout);

})
