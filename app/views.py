# jsonify creates a json representation of the response
from flask import Flask, render_template, redirect, request, jsonify
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask import url_for
from app import app

# importing posrgres  modules from the driver we just installed

import psycopg2

def build_postgres_connection():
    return psycopg2.connect(host='ec2-35-160-87-160.us-west-2.compute.amazonaws.com',
                            database='gis', user='postgres',
                            password='berkeley')

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
