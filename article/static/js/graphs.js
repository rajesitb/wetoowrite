$(document).ready(function () {

var chart = new CanvasJS.Chart("chartContainer", {
                animationEnabled: true,
                title: {
                    text: "Flu: Infected vs Deaths"
                },
                axisY: {
                    title: "Affected (Millions)",
                    titleFontColor: "#4F81BC",
                    lineColor: "#4F81BC",
                    labelFontColor: "#4F81BC",
                    tickColor: "#4F81BC"
                },
                axisY2: {
                    title: "Died (Millions)",
                    titleFontColor: "#C0504E",
                    lineColor: "#C0504E",
                    labelFontColor: "#C0504E",
                    tickColor: "#C0504E"
                },
                toolTip: {
                    shared: true
                },
                legend: {
                    cursor: "pointer",
                    itemclick: toggleDataSeries
                },
                data: [{
                    type: "column",
                    name: "Cases Infected (mn)",
                    legendText: "Infected Cases",
                    showInLegend: true,
                    dataPoints: [
                        {label: "Spanish Flu", y: 500},
                        {label: "Asian Flu", y: 500},
                        {label: "Hong Kong Flu", y: 300},
                        {label: "Swine Flu", y: 60}

                    ]
                },
                    {
                        type: "column",
                        name: "Death Cases (mn)",
                        legendText: "Death",
                        axisYType: "secondary",
                        showInLegend: true,
                        dataPoints: [
                            {label: "Spanish Flu", y: 50},
                            {label: "Asian Flu", y: 1.1},
                            {label: "Hong Kong Flu", y: 1.1},
                            {label: "Swine Flu", y: 0.575}
                        ]
                    }]
            });
            chart.render();

            function toggleDataSeries(e) {
                if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
                    e.dataSeries.visible = false;
                } else {
                    e.dataSeries.visible = true;
                }
                chart.render();
            }


            var chart1 = new CanvasJS.Chart("Container1", {
                animationEnabled: true,
                title: {
                    text: "Respiratory Syndrome: Infected vs Deaths"
                },
                axisY: {
                    title: "Affected/Died (Mil)",
                    titleFontColor: "#4F81BC",
                    lineColor: "#4F81BC",
                    labelFontColor: "#4F81BC",
                    tickColor: "#4F81BC"
                },
                axisY2: {
                    title: "Died (Thousands)",
                    titleFontColor: "#C0504E",
                    lineColor: "#C0504E",
                    labelFontColor: "#C0504E",
                    tickColor: "#C0504E"
                },
                toolTip: {
                    shared: true
                },
                legend: {
                    cursor: "pointer",
                    itemclick: toggleDataSeries
                },
                data: [{
                    type: "column",
                    name: "Infected Cases (Th) ",
                    legendText: "Infected Cases",
                    showInLegend: true,
                    dataPoints: [
                        {label: "SARS", y: 8},
                        {label: "MERS", y: 2.519},
                        {label: "COVID - 19", y: 6931},

                    ]
                },
                    {
                        type: "column",
                        name: "Death Cases (Th)",
                        legendText: "Death",
                        axisYType: "secondary",
                        showInLegend: true,
                        dataPoints: [
                            {label: "SARS", y: 0.8},
                            {label: "MERS", y: 0.7},
                            {label: "COVID - 19", y: 400},
                        ]
                    }]
            });
            chart1.render();

            function toggleDataSeries(e) {
                if (typeof (e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
                    e.dataSeries.visible = false;
                } else {
                    e.dataSeries.visible = true;
                }
                chart.render();
            }

})