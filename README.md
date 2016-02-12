# Loxo

## What is Loxo?
Loxo is a queryable GeoJSON API. Loxo digest various geographic formats (shapefiles, KML, CSV, geojson) and aims to turn them into a nice set of
intuitive endpoints that make dealing with geographic data easy.

## How does it work?
Lets say we ingest a geojson file called cupcakes.geojson which contains a selection of point data representing cupcakes shops in Portland. We can do a variety
of operations to access that data in different manners.

Return the GeoJSON as is:

    loxo/cupcakes/collections/cupcakes

The closest distance between any two points:

    loxo/cupcakes/collections/cupcakes/stats/minDistance

The points within the donut expressed (point, exclusion zone, donut radius):

    loxo/cupcakes/collections/cupcakes?withinDonut=-122.65335738658904,45.512083676585156,100,5000


## How do I set it up?
Install MongoDB and run the loxoapi.py file. Make sure you install the dependencies (I need to setup a requirements.txt)

## License
MIT License (see LICENSE)
