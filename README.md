# Loxo

## What is Loxo?
Loxo is a queryable GeoJSON API. Loxo digest various geographic formats (shapefiles, KML, CSV, geojson) and aims to turn them into a nice set of
intuitive endpoints that make dealing with geographic data easy.

## What is GeoJSON
GeoJSON is a way of encoding geographic information. It uses the JSON (JavaScript Object Notation) and therefor works out of the box with JavaScript.

* [Specification](http://geojson.org/geojson-spec.html)
* [geojson.io](http://www.geojson.io)

## How does it work?
Loxo has an upload page (loxo/upload) that lets users to ingest their data into Loxo. Lets say we ingest a geojson file called cupcakes.geojson which contains a selection of point data representing cupcakes shops in Portland. We can do a variety of operations to access that data in different manners.

Return the GeoJSON as is:

    loxo/cupcakes/collections/cupcakes

Get geometries within a specified proximit from a WGS84 longitude and latitude:

    loxo/cupcakes/collections/cupcakes?withinProximity=-122.65335738658904,45.512083676585156,1000

The points within the donut expressed (point, exclusion zone, donut radius):

    loxo/cupcakes/collections/cupcakes?withinDonut=-122.65335738658904,45.512083676585156,100,5000

The closest distance between any two points:

    loxo/cupcakes/collections/cupcakes/stats/minDistance

The stats endpoint also supports the following geo statistical operations:

    * Moran's I (Spatial Autocorrelation)
    * Geary's C (Spatial Autocorrelation)
    * Inverse Distance Weighting (IDW Interpolation)

## How do I set it up?
Install MongoDB and run the loxoapi.py file. Make sure you install the dependencies (I need to setup a requirements.txt)

## What about the docs?
I know, I know, I'll get something up ASAP.

## What's on the roadmap?

    * Docker
    * Docs
    * Authentication

## License
MIT License (see LICENSE)
