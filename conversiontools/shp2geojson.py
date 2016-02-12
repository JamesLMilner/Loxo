import sys
from json import dumps
import shapefile
import traceback

def shapefile_to_geojson(input_shp, output_name):
    ''' Takes point data in CSV format, with some form of position fields and converts them to GeoJSON'''

    # read the shapefile
    reader = shapefile.Reader(input_shp)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom, properties=atr))

    # write the GeoJSON file

    geojson = open(output_name + ".geojson", "w")
    geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    geojson.close()

    ## Based on code from http://geospatialpython.com/2013/07/shapefile-to-geojson.html
    ## Joel Lawhead 2013

if __name__ == '__main__':

    try:
        if len(sys.argv) == 1:
            print "Input Shapefile not specified"
        elif len(sys.argv) == 2:
            print "Input Shapefile specified as", sys.argv[1], ". Output GeoJSON file name not specified"
        else:
            input_shp = str(sys.argv[1])
            output_name = str(sys.argv[2])
            print "Converting", input_shp, "to", output_name + ".geojson"
            shapefile_to_geojson(input_shp, output_name)
            print "...Done!"

    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error, "\n"
        print traceback.format_exc()