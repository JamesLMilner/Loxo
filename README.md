# Loxo

## What is Loxo?
Loxo is a queryable GeoJSON API. Loxo digest various geographic formats (shapefiles, KML, CSV, geojson) and aims to turn them into a nice set of
intuitive endpoints that make dealing with geographic data easy.

!["A demo of the API"](/docs/demo.gif "A demo gif")

Loxo supports the following file formats for ingestion:

* Shapefile
* GeoJSON
* KML
* CSV (Points)

## What is GeoJSON?
GeoJSON is a way of encoding geographic information. It uses the JSON (JavaScript Object Notation) and therefor works out of the box with JavaScript.

* [Specification](http://geojson.org/geojson-spec.html)
* [geojson.io](http://www.geojson.io)

## How does it work?
Loxo has an upload page (loxo/upload) that lets users to ingest their data into Loxo. Lets say we ingest a geojson file called cupcakes.geojson which contains a selection of point data representing cupcakes shops in Portland. We can do a variety of operations to access that data in different manners.

Return the GeoJSON as is:

    loxo/cupcakes/collections/cupcakes

Get geometries within a specified proximity from a point:

    loxo/cupcakes/collections/cupcakes?withinProximity=-122.65335738658904,45.512083676585156,1000

The points within the donut expressed (point, exclusion zone, donut radius):

    loxo/cupcakes/collections/cupcakes?withinDonut=-122.65335738658904,45.512083676585156,100,5000

The points within a given polygon:

    /loxo/cupcakes/collections/cupcakes?withinPolygon= [ [ -122.64759063720702, 45.56526572302386 ], [ -122.662353515625, 45.53833906419679 ], [ -122.607421875, 45.50261730748197 ], [ -122.60175704956053, 45.5670683866382 ], [ -122.6436424255371, 45.576200993222955 ], [ -122.64759063720702, 45.56526572302386 ] ]

The closest distance between all points in a set of points:

    loxo/cupcakes/collections/cupcakes/stats/minDistance

The stats endpoint also supports the following geo statistical operations:

    * Moran's I (Spatial Autocorrelation)
    * Geary's C (Spatial Autocorrelation)
    * Inverse Distance Weighting (IDW Interpolation)


## Caveats
Loxo currently only handles geometries in the WGS84 coordinate system (as this is what GeoJSON and MongoDB use). Some end points haven't been fully tested with different geometry types so may fail.

## How do I set it up?

Using Docker:

    docker build
    docker up

If you're on Windows you will need to run this beforehand also:

    docker run --rm -i -t -p 80:80 nginx

Without Docker:

Download and install MongoDB, run the service and then run the loxoapi.py file. Make sure you install the dependencies (I need to setup a requirements.txt)

## What about the docs?
I know, I know, I'll get something up ASAP.

## What's on the roadmap?

    * Clarifying this readme
    * Docs
    * Authentication

## License
MIT License (see LICENSE)
