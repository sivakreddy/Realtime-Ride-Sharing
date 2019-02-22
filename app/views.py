# jsonify creates a json representation of the response
from flask import Flask, render_template, redirect, request, jsonify
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask import url_for
from app import app

# importing posrgres  modules from the driver we just installed

import psycopg2

def config(section):
    # create a parser
    parser = ConfigParser()
    # read config file
    filename = '../config.ini'
    parser.read(filename)

    # get section,
    config_params = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config_params[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config_params


def build_postgres_connection():


    try:
        db_params = config('postgres')
        return psycopg2.connect(host=db_params['host'],
                                database=db_params['database'],
                                user=db_params['user'],
                                password=db_params['password'])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Setting up connections to postgres

@app.route('/')
@app.route('/index')
def index():
       user = { 'nickname': 'Siva' } # fake user
       return render_template("index.html", title = 'Home',user = user)

@app.route('/api')
def get_trips():
       connection = build_postgres_connection()
       cursor = connection.cursor()
       query = "select * from rider_requests order by trip_id desc limit 100;"
       cursor.execute(query)
       response = cursor.fetchall()
       
       response_list = []
       for val in response:
            response_list.append(val)
       jsonresponse = [{"driver_start_lat": x[7], "driver_start_long": x[6], "driver_end_lat": x[9], "driver_end_long": x[8],"rider_start_lat": x[11],"rider_start_long": x[10], "rider_end_lat": x[13], "rider_end_long": x[12] } for x in response_list]
#       return jsonify(trips=jsonresponse)
       return render_template("trips_on_map_test.html", title = "Mathed Trips",trips = jsonresponse)
