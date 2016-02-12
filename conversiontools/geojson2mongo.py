import json
from pymongo import MongoClient
import sys
from os import path
import traceback


def feature_collection_to_mongodb(database, file_name, collection_name=None):
    print file_name
    client = MongoClient('localhost', 27017)
    db = client[database]
    if not collection_name:
        collection_name = path.splitext(path.basename(file_name))[0]
    if not file_name.endswith(".geojson"):
       file_name += ".geojson"
    with open(file_name) as data_file:
        data = json.load(data_file)
        features = data["features"]
        id = 0
        for feature in features:
            print feature
            feature["properties"]["loxo_id"] = id
            db[collection_name].insert(feature)
            id += 1

if __name__ == '__main__':

    try:
        if len(sys.argv) == 2:
            print "Input GeoJSON and target collection name not specified"
        elif len(sys.argv) == 3:
            print "Target collection name not specified for", sys.argv[1]
        elif len(sys.argv) == 4:
            database = str(sys.argv[1])
            filename = str(sys.argv[2])
            collection_name = sys.argv[3]
            print "Processing: \n", filename, "\nPushing into ", database, " as ", collection_name
            feature_collection_to_mongodb(database, filename, collection_name)
            print "GeoJSON successfully loaded into database", database, "as", collection_name
        else:
            raise Exception('Too many arguments passed')

    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error
        print traceback.format_exc()