import json
import sys

def validate_geojson_from_url(geojson_file, file=True):
    ''' Checks if GeoJSON file is valid; returns True if correct or False if invalid '''

    with open(geojson_file) as data_file:
        data = json.load(data_file)
        #print data
        return validate_geojson_from_dict(data)

def validate_geojson_from_file(geojson_file, file=True):
    ''' Checks if GeoJSON file is valid; returns True if correct or False if invalid '''

    with open(geojson_file) as data_file:
        data = json.load(data_file)
        #print data
        return validate_geojson_from_dict(data)

def validate_geojson_from_dict(data):
    ''' Checks if GeoJSON in dictionary form is valid; returns True if correct or False if invalid '''

    #http://geojson.org/geojson-spec.html
    VALID_FEATURES = ["Point", "LineString", "Polygon", "MultiPoint", "MultiLineString","MultiPolygon", "GeometryCollection"]

    features = data["features"]
    if not features:
        return False

    for feature in features:
        try:
            if not feature["type"]:
                print "The feature: ", feature, "has no type field!"
                return False
            if not feature["properties"]:
                print "The feature: ", feature, "has no properties field!"
                return False
            if not feature["geometry"]:
                print "The feature: ", feature, "has no geometry!"
                return False
            if not feature["geometry"]["type"]:
                print "The feature: ", feature, "has no type!"
                return False
            if feature["geometry"]["type"] not in VALID_FEATURES:
                print "The feature: ", feature, "does not have a valid type! Must be in :", VALID_FEATURES
                return False
            if not feature["geometry"]["coordinates"]:
                print "The feature: ", feature, "has no coordinates!"
                return False
            if feature["geometry"]["type"] == "Point" and len(feature["geometry"]["coordinates"]) < 2:
                print "The feature: ", feature, "has less than one coordinate (i.e. missing x or y)"
                return False
            if feature["geometry"]["type"] != "Point" and len(feature["geometry"]["coordinates"][0]) < 1:
                print "The feature: ", feature, "has less than one set of coordinate points"
                return False
            if feature["geometry"]["type"] == "Point":
                for coord in feature["geometry"]["coordinates"]:
                    try:
                        float(coord)
                    except ValueError:
                        print coord, "in", feature, "is not a float"
                        return False
            if feature["geometry"]["type"] == "LineString":
                for pair in feature["geometry"]["coordinates"]:
                    try:
                        float(pair[0])
                        float(pair[1])
                    except ValueError:
                        print pair, "in", feature, "contains none float"
                        return False
            if feature["geometry"]["type"] == "Polygon":
                for parts in feature["geometry"]["coordinates"]:
                    print parts
                    for part in parts:
                        try:
                            print part
                            float(part[0])
                            float(part[1])
                        except ValueError:
                            print parts, "in", feature, "contains none float"
                            return False
        except KeyError:
            return False # The property was not found so we know the GeoJSON is malformed

    return True


if __name__ == '__main__':

    try:
        if len(sys.argv) == 1:
            print "Input GeoJSON not specified"
        elif len(sys.argv) == 2:
            input_geojson = str(sys.argv[1])
            valid = validate_geojson_from_file(input_geojson)
            if valid:
                print "True: The GeoJSON is well formed and valid!"
            elif not valid:
                print "False: The GeoJSON is not well formed and/or valid!"
    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error