"use strict";


(function() {

    const dbServer = "http://192.168.178.23:443/";

    function fetchPowerConsumption() {
        return fetch(
            dbServer,
            {
                method: "GET", mode: "cors"
            }
        ).then(response => {
            return response.json();
        })
    }

    window.apiServices = {
        fetchPowerConsumption
    }

})();