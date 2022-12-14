"use strict";


(function() {

    const webAPI = "http://192.168.178.22:443/";

    function fetchPowerConsumption() {
        return fetch(
            webAPI,
            {
                method: "GET", mode: "cors"
            }
        ).then(response => {
            // if (!response.ok) {
            //     // console.log(response.statusText)
            //     // throw new Error(
            //     //     `fetch hat nicht funktioniert, das ist die Response vom Server: ${response.json()}`);
            // }
            return response.json();
        })
    }

    window.apiServices = {
        fetchPowerConsumption
    }

})();