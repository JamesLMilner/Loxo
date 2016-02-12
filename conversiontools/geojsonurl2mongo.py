from pymongo import MongoClient
import requests
from os import path
import sys

def feature_collection_endpoint_to_mongodb(database, url, collection_name=None):

    client = MongoClient('localhost', 27017)
    db = client[database]
    if not collection_name:
        collection_name = path.splitext(path.basename(url))[0]
    features = requests.get(url).json()["features"]
    # print features
    for feature in features:
        db[collection_name].insert(feature)

            
if __name__ == '__main__':

    try:
        database = str(sys.argv[1])
        url = str(sys.argv[2])
        collection_name = sys.argv[3]
        print "Downloading and processing: \n", url, "\nPushing into ", database, " as ", collection_name
        feature_collection_endpoint_to_mongodb(database, url, collection_name)
        print "GeoJSON successfully loaded into database", database, "as", collection_name

    except:
        error = sys.exc_info()[0]
        print "There was an error: ", error
