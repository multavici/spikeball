var icon_url = 'https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-128.png'; //'/img/marker-icon.png'
var coordinates = $('.coordinates');
var n = coordinates.length;

var lonLats = [];
console.log(lonLats);

map = new OpenLayers.Map("map");
map.addLayer(new OpenLayers.Layer.OSM());

for (i = 0; i < n; i++) {
    lonLats[i] = new OpenLayers.LonLat( $(coordinates[i]).data("longitude"), $(coordinates[i]).data("latitude") )
        .transform(
            new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
            map.getProjectionObject() // to Spherical Mercator Projection
        );
}
console.log(lonLats)

var centerLonLat = new OpenLayers.LonLat( 3.7236719, 51.0504707 )
    .transform(
        new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
        map.getProjectionObject() // to Spherical Mercator Projection
    );
    
var zoom=13;

var createMarkerIcon = function() {
    var iconSize = new OpenLayers.Size(32, 32)
    var iconOffset = new OpenLayers.Pixel(-(iconSize.w / 2), -iconSize.h)
    var icon = new OpenLayers.Icon(icon_url, iconSize, iconOffset)

    return icon
}

var markerIcon = createMarkerIcon()

var markers = new OpenLayers.Layer.Markers( "Markers" );
map.addLayer(markers);

for (i = 0; i < n; i++) {
    markers.addMarker(new OpenLayers.Marker(lonLats[i], markerIcon.clone()));
}

map.setCenter (centerLonLat, zoom);