$.fn.locationPicker = function(options) {

    var $this = this
    var settings = $.extend({
        map_el: '[data-type="map"]',
        lat_el: '[id="latitude"]',
        long_el: '[id="longitude"]',
        raw_data: false,
        init: {
            location : {latitude:51.0543422, longitude:3.7174243} // put initial location here
        }
    }, options)

    var data = {}

    var mapEl = $(settings.map_el)
    var latEl = $(settings.lat_el)
    var longEl = $(settings.long_el)
    var init_zoom = 13
    var zoom = null
    var icon_url = 'https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-128.png' //'/img/marker-icon.png'

    var createMarkerIcon = function() {
        var iconSize = new OpenLayers.Size(32, 32)
        var iconOffset = new OpenLayers.Pixel(-(iconSize.w / 2), -iconSize.h)
        var icon = new OpenLayers.Icon(icon_url, iconSize, iconOffset)

        return icon
    }

    var markerIcon = createMarkerIcon()

    var generateRandId = function() {
        var randLetter = String.fromCharCode(65 + Math.floor(Math.random() * 26))
        var id = randLetter + Date.now()
        return id
    }

    var saveData = function() {
        if (latEl.length > 0) {
            latEl.val(data.location.lat)
        }
        if (longEl.length > 0) {
            longEl.val(data.location.long)
        }
    }

        /* Open Street Map config */
    var setMapLocation = function(lat, long, centerMap) {

        if (centerMap === undefined) centerMap = true

        var latLong = new OpenLayers.LonLat(long, lat).transform(
            new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
            map.getProjectionObject() // to Spherical Mercator Projection
        )

        if (!zoom) {
            zoom = init_zoom
        } else {
            zoom = map.getZoom()
        }

        if (centerMap) {
            map.setCenter(latLong, zoom)
        }

        marker = new OpenLayers.Marker(latLong, markerIcon)

        markers.clearMarkers()
        markers.addMarker(marker)
    }

    OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
        defaultHandlerOptions: {
            'single': true,
            'double': false,
            'pixelTolerance': 0,
            'stopSingle': false,
            'stopDouble': false
        },

        initialize: function(options) {
            this.handlerOptions = OpenLayers.Util.extend({}, this.defaultHandlerOptions)
            OpenLayers.Control.prototype.initialize.apply(
                this, arguments
            )
            this.handler = new OpenLayers.Handler.Click(
                this, {
                    'click': this.trigger
                }, this.handlerOptions
            )
        },

        trigger: function(e) {
            var latLong = map.getLonLatFromPixel(e.xy).transform(
                    map.getProjectionObject(),
                    new OpenLayers.Projection("EPSG:4326")) // transform to WGS 1984

            data = {
                location: {
                    lat: latLong.lat,
                    long: latLong.lon
                }
            }

            setMapLocation(data.location.lat, data.location.long, false)
            onLocationChanged()
        }

    })

    var mapId = mapEl.attr('id')
    if (!mapId) {
        mapEl.attr('id', generateRandId())
    }

    var map = new OpenLayers.Map(mapEl.attr('id'))
    map.addLayer(new OpenLayers.Layer.OSM())

    var markers = new OpenLayers.Layer.Markers("Markers")
    map.addLayer(markers)

    var click = new OpenLayers.Control.Click()
    map.addControl(click)
    click.activate()

    var marker = null

    this.getData = function() {
        return data
    }

    this.getAddress = function() {
        return data.formatted_address
    }

    var init = function() {
        if (settings.init) {
            setMapLocation(settings.init.location.latitude, settings.init.location.longitude)
        }
    }

    var onLocationChanged = function() {
        saveData()
        console.log(data.location.lat)

        if (settings.locationChanged) {
            settings.locationChanged(data)
        }
    }

    init()

    return this
}