import csv
import json
import sys
import traceback

def csv_to_geojson(input_csv, output_name):
    ''' Takes point data in CSV format, with some form of position fields and converts them to GeoJSON'''

    print input_csv, output_name

    X_COLUMNS = ["lng", "longitude", "long", "lon", "x", "X", "X coordinate", "x coordinate", "easting", "Easting"]
    Y_COLUMNS = ["lat", "latitude", "y", "Y", "Y Coordinate", "y coordinate", "northing", "Northing" ]

    with open(input_csv, 'rb') as file:
        features = []
        reader = csv.reader(file)
        row_counter = 0
        for row in reader:
            if row_counter == 0:
                column_counter = 0
                fields = row
                for column in row:
                    if column in X_COLUMNS:
                        x_column = column_counter
                    if column in Y_COLUMNS:
                        y_column = column_counter
                    column_counter += 1

                if not x_column and not y_column:
                    raise ValueError('A very specific bad thing happened')
            else:
                x = row[x_column]
                y = row[y_column]
                field_counter = 0
                properties = { }
                for field in fields:
                    if field != fields[x_column] or field != fields[x_column]:
                        properties[field] = row[field_counter]
                    field_counter += 1
                feature = {
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [float(x), float(y)]},
                            "properties": properties
                          }
                features.append(feature)


            row_counter += 1

        output =  { "type": "FeatureCollection", "features": features }
        if not output_name.endswith(".geojson"):
            output_name += ".geojson"
        with open(output_name, 'w') as outfile:
            json.dump(output, outfile, indent=4)

        return output_name

if __name__ == '__main__':

     try:
        if len(sys.argv) == 1:
            print "Input CSV not specified"
        elif len(sys.argv) == 2:
            print "Input CSV specified as", sys.argv[1], ". Output GeoJSON file name not specified"
        else:
            input_csv = str(sys.argv[1])
            output_name = str(sys.argv[2])
            print "Converting", input_csv, "to", output_name + ".geojson"
            out = csv_to_geojson(input_csv, output_name)
            print "...Done!"

     except:
        error = sys.exc_info()[0]
        print "There was an error: ", error, "\n"
        print traceback.format_exc()