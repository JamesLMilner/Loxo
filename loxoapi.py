from pymongo import MongoClient, GEO2D, DESCENDING, errors
from flask import Flask, make_response, request, Blueprint, render_template, redirect, url_for, send_from_directory
from bson.json_util import dumps
from werkzeug.utils import secure_filename
from ast import literal_eval
from bson.son import SON
import json
import os

from loxoutils import *
from loxostats import *
from loxoerrors import *

# Flask Setup
DB_DOWN = False
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['kml', 'zip', 'geojson', 'csv', "png"])

app = Flask(__name__)
app.register_blueprint(stats_api, url_prefix='/loxo/<database>/collections/<dataset>/stats')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# MongoDB Setup
try:
    mdb_port = 27017
    host = os.environ.get('LOXO_DB_1_PORT_27017_TCP_ADDR', 'localhost')
    client = MongoClient(host, mdb_port, serverSelectionTimeoutMS=1) #Checks to see if MDB is up
    client.server_info()

except errors.ServerSelectionTimeoutError as err:
    DB_DOWN = True
    print "MongoDB is down :", err


#API Endpoints

@app.route('/')
@app.route('/loxo/')
def loxo():
    """Return the Loxo welcome message, point to documentation."""
    return render_template('index.html')


@app.route('/loxo/viewer')
def viewer():
    """Show a map to view the GeoJSON returned from a Loxo endpoint"""
    return render_template('viewer.html')


@app.route('/loxo/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            filename = secure_filename(file.filename)
            file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print "file location", file_location
            file.save(file_location)
            saved_file = url_for('uploaded_file', filename=filename)

            endpoint_name = os.path.splitext(filename)[0]
            database = request.form.get("database")
            if not database:
                print request.form["database"]
                raise InvalidUsage("Database name was not provided", 400, '{ "error" : "database was not provided" }')
            else:
                handle_file(database, file_location, endpoint_name, host)

            return redirect('/loxo/' + database + '/collections/' + endpoint_name)

    return render_template('upload.html')


@app.route('/loxo/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/loxo/<database>/index/spatial', methods=['GET'])
def index_collections(database):
    """Peform Spatial Indexing on the Collections"""
    db = client[database]
    for collection in db.collection_names(include_system_collections=False):
        print "Indexing ", collection, "with a ", GEO2D, " index."
        db[collection].create_index( [("geometry.coordinates", GEO2D)], background=True )
    return make_response( json.dumps({"Spatial Index": "Finished"}) )


@app.route('/loxo/<database>/collections/<dataset>', methods=['GET'])
def get_data_by_value(database, dataset):
    """Return a dataset, based on parameters passed"""
    db = client[database]
    collection = db[dataset]

    if len(request.args) == 0:
        feature_collection = find_features(collection, {})
        return make_response(create_feature_collection(feature_collection))

    else:
        property = request.args.get("property")
        within_proximity = request.args.get("withinProximity")
        within_donut = request.args.get("withinDonut")
        within_polygon = request.args.get("withinPolygon")
        k_nearest = request.args.get("kNearest")

        # Handle Requests
        if property:
            get_property = "properties." + property
            return_features = find_features(collection, {get_property : request.args.get("value")})
            feature_collection = create_feature_collection(return_features)
            return make_response( feature_collection )

        if within_proximity and not property:
            args = within_proximity.split(",")
            lng = float(args[0])
            lat = float(args[1])
            proximity_radius = abs(float(args[2]))
            print proximity_radius
            proximity_radius_query = [[lng, lat], meters_to_radians(proximity_radius)]
            find = {"geometry.coordinates": {"$geoWithin": {"$centerSphere": proximity_radius_query }}}
            return_features = find_features(collection, find)
            feature_collection = create_feature_collection(return_features)
            return make_response( feature_collection )

        if within_donut and not property:
            args = within_donut.split(",")
            lng = float(args[0])
            lat = float(args[1])
            donut_min = meters_to_radians(abs(float(args[2])))
            donut_max = meters_to_radians(abs(float(args[3])))
            donut_query = { "$nearSphere": [lng, lat], "$minDistance" : donut_min, "$maxDistance": donut_max}
            find = { "geometry.coordinates": donut_query}
            return_features = find_features(collection, find) # Exclude the id field
            feature_collection = create_feature_collection(return_features)
            return make_response( feature_collection )

        if within_polygon and not property:

            #polygon = [ [0.0 , 0.0], [-180.0 , 0.0], [-180.0 , 90.0], [0.0 , 90.0] ]
            polygon = literal_eval(within_polygon) # http://stackoverflow.com/questions/1894269/convert-string-representation-of-list-to-list-in-python
            find = { "geometry.coordinates": {"$geoWithin": {"$polygon": polygon }} }
            return_features = find_features(collection, find)
            feature_collection = create_feature_collection(return_features)
            return make_response( feature_collection )

        if k_nearest and not property:
            args = k_nearest.split(",")
            lng = float(args[0])
            lat = float(args[1])
            distance_radius = abs(float(args[2]))
            #query = [{"$geoNear":{ "near": [lat, lng], "distanceField": "distance", "maxDistance": distance_radius}}]

            result = db.command(SON([('geoNear', dataset), ('near', [lng, lat]), ('num', distance_radius)]))["results"]
            feature_type = "Feature"
            results = []

            for parent_obj in result:
                print parent_obj
                print parent_obj["obj"]
                print type(parent_obj)
                obj = parent_obj["obj"]
                feature = { }
                feature["geometry"] = obj["geometry"]
                feature["type"] = feature_type
                feature["properties"] = obj["properties"]
                feature["properties"]["kNeartestDistance"] = parent_obj["dis"]
                results.append(feature)

            return create_feature_collection(results)


        if within_proximity and property or within_proximity and property:
            return "Sorry, property AND proximity searching not currently supported"

#Retrieve by ID
@app.route('/loxo/<database>/collections/<dataset>/<int:id>', methods=['GET'])
def get_data_by_id(database, dataset, id):
    db = client[database]
    collection = db[dataset]
    get_property = "properties.loxo_id"
    return_feature = find_features(collection, {get_property : id})
    return make_response( return_feature )

## Error handling
apply_error_handling(app)


if __name__ == '__main__':

    if DB_DOWN == False:
        if host == 'localhost':

            app.run(host='localhost')
        else:
            # DOCKER
            app.run(host='0.0.0.0')