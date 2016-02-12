import unittest
import os
from pymongo import MongoClient, GEO2D, DESCENDING
from bson import json_util
from conversiontools.csv2geojson import *
from conversiontools.kml2geojson import *
from conversiontools.shp2geojson import *
from conversiontools.validategeojson import *
from conversiontools.geojson2mongo import *
from conversiontools.geojsonurl2mongo import *


class conversionTest(unittest.TestCase):
    """TestCase for the API conversion module"""

    def setUp(self):
        self.data_input_folder = "data-load/example/"
        self.data_output_folder = "data-outputs/"
        self.database = "testdatabase"
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[self.database]
        os.chdir("../conversiontools")


    def validategeojson_test(self):
        """ Testing that GeoJSON validation functions correctly """

        valid_input_geojson =  self.data_input_folder + "cupcakes.geojson"
        invalid_input_geojson = self.data_input_folder + "cupcakesmalformed.geojson"
        self.assertTrue(validate_geojson_from_file(valid_input_geojson))
        self.assertFalse(validate_geojson_from_file(invalid_input_geojson))


    def csv2geojson_test(self):
        """ Testing that CSV correctly translates to GeoJSON """

        input_csv = self.data_input_folder + "significantmonth.csv"
        output_geojson = self.data_output_folder + "significantmonth.geojson"
        csv_to_geojson(input_csv, output_geojson)
        self.assertTrue(os.path.exists(output_geojson) == 1, msg="Current working directory is: , {0}".format(os.getcwd()) )
        num_lines = sum(1 for line in open(output_geojson))
        self.assertTrue(num_lines == 369)
        self.assertTrue(validate_geojson_from_file(output_geojson))


    def shp2geojson_test(self):
        """ Testing that Shapefile correctly translates to GeoJSON """

        input_shp = self.data_input_folder + "London Shapefile/Greater_London_Const_Region.shp"
        output_geojson = self.data_output_folder + "Greater_London_Const_Region"
        shapefile_to_geojson(input_shp, output_geojson)
        output_geojson_suffixed = output_geojson + ".geojson"
        self.assertTrue(os.path.exists(output_geojson_suffixed) == 1, msg="Current working directory is: {0}".format(os.getcwd()) )
        num_lines = sum(1 for line in open(output_geojson_suffixed))
        self.assertTrue(num_lines == 136195)
        self.assertTrue(validate_geojson_from_file(output_geojson_suffixed))


    def kml2geojson_test(self):
        """ Testing that CSV correctly translates to GeoJSON """

        input_kml = self.data_input_folder + "placemark.kml"
        output_geojson = self.data_output_folder + "placemark.geojson"
        kml_to_geojson(input_kml, output_geojson)
        num_lines = sum(1 for line in open(output_geojson))
        self.assertTrue(os.path.exists(output_geojson) == 1, msg="Current working directory is: , {0}".format(os.getcwd()) )
        self.assertTrue(num_lines == 19)
        self.assertTrue(validate_geojson_from_file(output_geojson))

    def geojson2mongo_test(self):
        """ Testing that GeoJSON correctly gets put into the MongoDB instance database """
        database = self.database
        db = self.db
        input_geojson = self.data_input_folder + "cupcakes.geojson"
        self.assertTrue(validate_geojson_from_file(input_geojson))
        feature_collection_to_mongodb(database, input_geojson, "testcupcakes")
        feature_collection = db["testcupcakes"].find({ })
        count = feature_collection.count()
        test_collection = json_util.dumps(feature_collection)
        self.assertTrue(count == 74, msg="Record count is " + str(count))

    def geojsonurl2mongo_test(self):
        """ Testing that GeoJSON correctly gets put into the MongoDB instance database """
        database = self.database
        db = self.db
        input_geojson_url = "https://raw.githubusercontent.com/lyzidiamond/learn-geojson/master/geojson/cupcakes.geojson"
        feature_collection_endpoint_to_mongodb(database, input_geojson_url, "testurlcupcakes")
        feature_collection = db["testurlcupcakes"].find({ })
        count = feature_collection.count()
        test_collection = json_util.dumps(feature_collection)
        self.assertTrue(count == 74, msg="Record count is " + str(count))

    def tearDown(self):
        self.db["testcupcakes"].drop();
        self.db["testurlcupcakes"].drop();

if __name__ == '__main__':
    unittest.main()