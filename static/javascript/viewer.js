
var map = L.map('map').setView([0, 0], 3);
var geoJsonLayer;

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


function onEachFeature(feature, layer) {
    // does this feature have a property named popupContent?
    var popupContent = "";
    var properties = feature.properties;
    if (properties) {
        for (var prop in feature.properties) {
           popupContent += "<b>" + prop + "</b> : " + properties[prop] + "<br>";
        }
    }
    layer.bindPopup(popupContent)
}

function viewGeoJson(element) {

    var url = document.getElementById("geojson-endpoint").value;
    console.log(url);
    $.get(url,
        function(geoJson) {
            if (geoJson) {
                var geoJsonFeatures = JSON.parse(geoJson);
                if (geoJsonLayer) {
                    map.removeLayer(geoJsonLayer)
                }
                geoJsonLayer = L.geoJson(geoJsonFeatures,{ onEachFeature: onEachFeature }).addTo(map);
                map.fitBounds(geoJsonLayer.getBounds());
            }
        }
    );
    return false;
}

$('#url-input').submit(function () {
    viewGeoJson(this);
    return false;
});

L.control.locate({
    position: 'topleft',  // set the location of the control
    layer: new L.LayerGroup(),  // use your own layer for the location marker
    drawCircle: true,  // controls whether a circle is drawn that shows the uncertainty about the location
    follow: false,  // follow the user's location
    setView: true, // automatically sets the map view to the user's location, enabled if `follow` is true
    keepCurrentZoomLevel: false, // keep the current map zoom level when displaying the user's location. (if `false`, use maxZoom)
    stopFollowingOnDrag: false, // stop following when the map is dragged if `follow` is true (deprecated, see below)
    remainActive: false, // if true locate control remains active on click even if the user's location is in view.
    markerClass: L.circleMarker, // L.circleMarker or L.marker
    circleStyle: {},  // change the style of the circle around the user's location
    markerStyle: {},
    followCircleStyle: {},  // set difference for the style of the circle around the user's location while following
    followMarkerStyle: {},
    icon: 'fa fa-map-marker',  // class for icon, fa-location-arrow or fa-map-marker
    iconLoading: 'fa fa-spinner fa-spin',  // class for loading icon
    circlePadding: [0, 0], // padding around accuracy circle, value is passed to setBounds
    metric: true,  // use metric or imperial units
    onLocationError: function(err) {alert(err.message)},  // define an error callback function
    onLocationOutsideMapBounds:  function(context) { // called when outside map boundaries
            alert(context.options.strings.outsideMapBoundsMsg);
    },
    showPopup: true, // display a popup when the user click on the inner marker
    strings: {
        title: "Show me where I am",  // title of the locate control
        metersUnit: "meters", // string for metric units
        feetUnit: "feet", // string for imperial units
        popup: "You are within {distance} {unit} from this point",  // text to appear if user clicks on circle
        outsideMapBoundsMsg: "You seem located outside the boundaries of the map" // default message for onLocationOutsideMapBounds
    },
    locateOptions: {}  // define location options e.g enableHighAccuracy: true or maxZoom: 10
}).addTo(map);