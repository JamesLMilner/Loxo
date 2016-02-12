import xml.dom.minidom as dom
from kml import kml
import json
import sys
import traceback

def kml_to_geojson(kml_file, output_name):

    kml_one = dom.parse(kml_file) # parse KML file using minidom
    if not output_name.endswith(".geojson"):
            output_name += ".geojson"
    with open( output_name, 'w') as outfile:
        output = kml.build_feature_collection(kml_one)
        json.dump(output, outfile, indent=4)


if __name__ == '__main__':

    try:
        if len(sys.argv) == 1:
            print "Input KML not specified"
        elif len(sys.argv) == 2:
            print "Input KML specified as", sys.argv[1], ". Output GeoJSON file name not specified"
        else:
            input_kml = str(sys.argv[1])
            output_name = str(sys.argv[2])
            print "Converting", input_kml, "to", output_name + ".geojson"
            kml_to_geojson(input_kml, output_name)
            print "...Done!"

    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error, "\n"
        print traceback.format_exc()