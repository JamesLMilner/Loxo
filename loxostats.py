from pymongo import MongoClient, GEO2D, DESCENDING
from flask import Flask, make_response, request,  Blueprint
from loxoutils import *
import json
from math import pow

#Flask Setup
client = MongoClient('localhost', 27017)
stats_api = Blueprint('stats_api', __name__)

@stats_api.route('/count', methods=['GET'])
def get_feature_count(database, dataset):
    """Return a datasets feature count"""
    db = client[database]
    return make_response( json.dumps({ "count" : db[dataset].count()}) )

@stats_api.route('/centroid', methods=['GET'])
def get_centroid(database, dataset):
    """Return centroid of a series of points"""
    db = client[database]
    collection = db[dataset]
    features = collection.find({ })

    #Compare all coordinates against all other coordinates (without duplicate comparisons)
    x_centroid = 0.0
    y_centroid = 0.0
    feature_count = 0

    for feature in features:
        feature_count += 1
        coords = feature["geometry"]["coordinates"]
        x_centroid += coords[0]
        y_centroid += coords[1]

    x = x_centroid / feature_count
    y = y_centroid / feature_count

    return make_response( json.dumps({ "Centroid" : {"x" : x, "y" : y} }) )


@stats_api.route('/averageDistance', methods=['GET'])
def get_average_distance(database, dataset):
    """Return the average distance between a datasets geometries"""
    db = client[database]
    collection = db[dataset]
    features = collection.find({ })

    #Compare all coordinates against all other coordinates (without duplicate comparisons)
    checked = set() # Use a set for checking purposes
    counter = 0
    distance = 0

    for f1 in features:
        counter += 1
        coords1 = tuple(f1["geometry"]["coordinates"])
        checked.add(coords1)
        for f2 in features:
            coords2 = tuple(f2["geometry"]["coordinates"])
            if coords2 not in checked:
                #Lon Lat for Mongo!
                distance += abs(get_WGS84_distance(coords1[1], coords1[0], coords2[1],coords2[0]))

    mean_distance = distance / counter
    return make_response( json.dumps({ "Average Distance (meters)" : mean_distance }) )


@stats_api.route('/minDistance', methods=['GET'])
def get_min_distance(database, dataset):
    """Return the average distance between a datasets geometries"""
    db = client[database]
    collection = db[dataset]
    features = collection.find({ })

    #Compare all coordinates against all other coordinates (without duplicate comparisons)
    checked = set() # Use a set for checking purposes
    counter = 0
    distance = 0
    min_distance = None

    for f1 in features:
        counter += 1
        coords1 = tuple(f1["geometry"]["coordinates"])
        checked.add(coords1)
        for f2 in features:
            coords2 = tuple(f2["geometry"]["coordinates"])
            if coords2 not in checked:
                #Lon Lat for Mongo!
                distance = abs(get_WGS84_distance(coords1[1], coords1[0], coords2[1],coords2[0]))
                if not min_distance or distance < min_distance:
                    min_distance = distance

    return make_response( json.dumps({ "Minimum Distance (meters)" : min_distance }) )


@stats_api.route('/maxDistance', methods=['GET'])
def get_max_distance(database, dataset):
    """Return the average distance between a datasets geometries"""

    db = client[database]
    collection = db[dataset]
    features = collection.find({ })

    #Compare all coordinates against all other coordinates (without duplicate comparisons)
    checked = set() # Use a set for checking purposes
    counter = 0
    distance = 0
    max_distance = 0

    for f1 in features:
        counter += 1
        coords1 = tuple(f1["geometry"]["coordinates"])
        checked.add(coords1)
        for f2 in features:
            coords2 = tuple(f2["geometry"]["coordinates"])
            if coords2 not in checked:
                #Lon Lat for Mongo!
                distance = abs(get_WGS84_distance(coords1[1], coords1[0], coords2[1],coords2[0]))
                if distance > max_distance:
                    max_distance = distance

    return make_response( json.dumps({ "Maximum Distance (meters)" : max_distance }) )


@stats_api.route('/totalDistance', methods=['GET'])
def get_total_distance(database, dataset):
    """Return the average distance between a datasets geometries"""
    db = client[database]
    collection = db[dataset]
    features = collection.find({ })

    #Compare all coordinates against all other coordinates (without duplicate comparisons)
    checked = set() # Use a set for checking purposes
    distance = 0

    for f1 in features:
        coords1 = tuple(f1["geometry"]["coordinates"])
        checked.add(coords1)
        for f2 in features:
            coords2 = tuple(f2["geometry"]["coordinates"])
            if coords2 not in checked:
                #Lon Lat for Mongo!
                distance += abs(get_WGS84_distance(coords1[1], coords1[0], coords2[1],coords2[0]))

    mean_distance = distance
    return make_response( json.dumps({ "Total Distance (meters)" : mean_distance }) )

@stats_api.route('/idw', methods=['GET'])
def get_idw_value(database, dataset):
    """Return the average distance between a datasets geometries"""
    db = client[database]
    collection = db[dataset]
    features = collection.find({ })

    target_point = request.args.get("interpPoint")
    point =  target_point.split(",")
    lng = float(point[0])
    lat = float(point[1])

    property = request.args.get("property")

    interpolated_value = idw(features, property, [lng, lat])

    return make_response( json.dumps( {"Point" : [lng, lat], "Interpolated Value" : interpolated_value } ) )



@stats_api.route('/moransI', methods=['GET'])
def get_morans_i(database, dataset):
    """Return the Morans I for a given attribute"""

    attribute = request.args.get("attribute")

    if len(request.args) == 0:
        return "You must specify the attribute parameter!"

    elif len(request.args) == 1 and attribute:
        db = client[database]
        collection = db[dataset]

        features = loads(dumps(collection.find({}, EXCLUDE_ID)))
        I = morans_i(features, attribute)
        return str(I)

@stats_api.route('/gearysC', methods=['GET'])
def get_gearys_c(database, dataset):
    """Return the Morans I for a given attribute"""

    attribute = request.args.get("attribute")

    if len(request.args) == 0:
        return "You must specify the attribute parameter!"

    elif len(request.args) == 1 and attribute:
        db = client[database]
        collection = db[dataset]

        features = loads(dumps(collection.find({}, EXCLUDE_ID)))
        C = gearys_c(features, attribute)
        return str(C)

def morans_i(points, attribute):

    try:

        weights_sum = 0.0   #S0
        n = float(len(points))   #n
        numerator = 0.0    #top part
        denominator = 0.0   #bottom part

        # Calculate the mean of our attribute (x bar)
        x_mean = 0.0 #x bar
        for x in points:
            x_mean += float(x["properties"][attribute])
        x_mean = x_mean / n

        print "X MEAN: ", x_mean

        # Double Sigma sum notation
        for i in points:
            lng1 = i["geometry"]["coordinates"][0]
            lat1 = i["geometry"]["coordinates"][1]
            i_attribute = float(i["properties"][attribute])
            denominator += pow((i_attribute - x_mean), 2)

            for j in points:
                lng2 = j["geometry"]["coordinates"][0]
                lat2 = j["geometry"]["coordinates"][1]
                j_attribute = float(j["properties"][attribute])
                d = get_WGS84_distance(lat1, lng1, lat2, lng2) # Distance

                wij = 1 / 1 + d #pow( 1 + d, 1 )
                weights_sum += wij

                numerator += ( wij * (i_attribute - x_mean) * (j_attribute - x_mean) )

        print weights_sum, n
        n_over_weights = n / weights_sum
        print numerator, denominator
        I = n_over_weights * (numerator / denominator)
        return I

    except TypeError:
        return "Attribute is none numerical"


def gearys_c(points, attribute):

    try:
        C = 0.0
        n = float(len(points))   #n
        numerator = 0.0    #top part
        denominator = 0.0   #bottom part
        weights_sum = 0.0

        # Calculate the mean of our attribute (x bar)
        x_mean = 0.0 #x bar
        for x in points:
            x_mean += float(x["properties"][attribute])
        x_mean = x_mean / n

        # Double Sigma sum notation
        for i in points:
            lng1 = i["geometry"]["coordinates"][0]
            lat1 = i["geometry"]["coordinates"][1]
            i_attribute = float(i["properties"][attribute])
            denominator += pow((i_attribute - x_mean), 2)

            for j in points:
                lng2 = j["geometry"]["coordinates"][0]
                lat2 = j["geometry"]["coordinates"][1]
                j_attribute = float(j["properties"][attribute])
                d = get_WGS84_distance(lat1, lng1, lat2, lng2) # Distance

                wij = 1 / 1 + d #pow( 1 + d, 1 )
                weights_sum += wij

                numerator += (wij * pow( (i_attribute - x_mean), 2))


        numerator = (n - 1) * numerator
        denominator = 2 * weights_sum * denominator
        C = numerator / denominator

        return C

    except TypeError:
        return "Attribute is none numerical"



def idw(points, variable, interp_point):

    lon2 = float(interp_point[0])
    lat2 = float(interp_point[1])
    numerator = 0
    denominator = 0

    for known_point in points:
        lon1 = float(known_point["geometry"]["coordinates"][0])
        lat1 = float(known_point["geometry"]["coordinates"][1])
        known_point_variable = known_point["properties"][variable]
        if not is_float(known_point_variable):
            return "Variable", known_point_variable, "is not numeric; it cannot be interpolated"
        distance = get_WGS84_distance( lat1, lon1, lat2, lon2 )
        numerator += 1 / distance * float(known_point_variable)
        denominator += 1 / distance

    v = numerator / denominator

    return v

def is_float(value):
  try:
    float(value)
    return True
  except:
    return False