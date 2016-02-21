from json import *
from bson.json_util import dumps
from geographiclib.geodesic import Geodesic
from conversiontools.csv2geojson import *
from conversiontools.geojson2mongo import *

EARTH_RADIUS = 6378.1
GEO_DIST = "s12" # How geographiclib calls distance?
EXCLUDE_ID = {"_id": 0 }

def create_feature_collection(return_features):
    arg_type = type(return_features)
    if arg_type != list and arg_type == str:
        return dumps({ "type": "FeatureCollection", 'features':  loads(return_features) }, indent=4 )
    elif arg_type == list:
        return dumps({ "type": "FeatureCollection", 'features':  return_features }, indent=4 )

def meters_to_radians(meters):
    rads = float(meters / 1000) / EARTH_RADIUS
    return rads

def get_WGS84_distance( lat1, lon1, lat2, lon2 ):
    return Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2, Geodesic.DISTANCE)[GEO_DIST]

def find_features(collection, findDict):
    return dumps(collection.find(findDict, EXCLUDE_ID))

def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_file_type(filename):
    return filename.rsplit('.', 1)[1]

def handle_file(db, filename, endpoint_name, host):
    file_type = get_file_type(filename)
    if file_type == "csv":
        file = csv_to_geojson(filename, "./uploads/" + endpoint_name)
    if file_type == "geojson":
        file = filename

    feature_collection_to_mongodb(db, file, collection_name=endpoint_name, host=host)

