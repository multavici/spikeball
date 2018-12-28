// TODO: Add popup like this: http://dev.openlayers.org/examples/osm-marker-popup.html
var icon_url = 'https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-128.png' //'/img/marker-icon.png'
var longitude = $('#coordinates').data("longitude");
var latitude = $('#coordinates').data("latitude");


map = new OpenLayers.Map("map");
map.addLayer(new OpenLayers.Layer.OSM());

var lonLat = new OpenLayers.LonLat( longitude, latitude )
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

markers.addMarker(new OpenLayers.Marker(lonLat, markerIcon));

map.setCenter (lonLat, zoom);