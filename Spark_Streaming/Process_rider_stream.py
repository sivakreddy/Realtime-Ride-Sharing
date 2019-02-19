
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SQLContext
import psycopg2
from configparser import ConfigParser

#method to read config file for system parameters
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

#Connection to PostgreSQL
def build_postgres_connection():

    try:
        db_params = config('postgres')
        return psycopg2.connect(host=db_params['host'],
                                database=db_params['database'],
                                user=db_params['user'],
                                password=db_params['password'])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

#Getting nearest node to the location
def nearest_node(cursor, long,lat):
    query = """
            SELECT source from ways order by  the_geom <-> ST_SetSrid(ST_MakePoint(%s, %s), 4326) limit 1;
            """
    data = (long, lat)
    cursor.execute(query, data)
    node_list = cursor.fetchall()
    return node_list[0][0]

#Calculating driving distance between two nodes
def calc_driving_distance(cursor, start_node,end_node):
    if start_node == end_node:
        return 0
    else:

        query = """
                SELECT sum(cost) FROM pgr_dijkstra(
                'SELECT gid AS id,
                     source,
                     target,
                     cost_s AS cost,
                     reverse_cost_s AS reverse_cost
                    FROM ways',
                %s,%s, directed := true);
                """
        data = (start_node,end_node)
        cursor.execute(query, data)
        distance = cursor.fetchall()
        # print(distance[0][0])
        try:
            float(distance[0][0])
            return float(distance[0][0])
        except Exception as err:
            return 9999999999999

#processing rider stream to match with driver
def process_rider_messages(rdd):
    connection = build_postgres_connection()
    cursor = connection.cursor()

    for line in rdd:
        trip_id, start_location_long, start_location_lat, end_location_long, end_location_lat, status = line[:]
        #finding nearest three drivers
        query = """
                select trip_id, (ST_Distance(driver_location, 'SRID=4326;POINT(%s %s)') + 
                ST_Distance(driver_destination, 'SRID=4326;POINT(%s %s)')) as total_distance,
                start_long, start_lat, end_long, end_lat
                from driver_location 
                order by (ST_Distance(driver_location, 'SRID=4326;POINT(%s %s)') + 
                ST_Distance(driver_destination, 'SRID=4326;POINT(%s %s)'))
                limit 3;
                """

        data = (float(start_location_long), float(start_location_lat), float(end_location_long),
                float(end_location_lat), float(start_location_long), float(start_location_lat),
                float(end_location_long), float(end_location_lat))
        cursor.execute(query, data)
        nearest_drivers = cursor.fetchall()
        # print(nearest_drivers)
        best_detour = 9999999999999
        best_match_driver = None
        for driver in nearest_drivers:
            d_trip_id, d_total_distance, d_start_long, d_start_lat, d_end_long, d_end_lat = driver[:]

            d_start_node = nearest_node(cursor, float(d_start_long),float(d_start_lat)) #driver start node
            d_end_node = nearest_node(cursor, float(d_end_long), float(d_end_lat)) #driver end node
            r_start_node = nearest_node(cursor, float(start_location_long),float(start_location_lat)) #rider start node
            r_end_node = nearest_node(cursor, float(end_location_long), float(end_location_lat)) #rider end node


            d_original_distance = calc_driving_distance(cursor,d_start_node, d_end_node) #Driver original driving distance
            d_new_distance = calc_driving_distance(cursor,d_start_node, r_start_node) \ #Driving distance if ride is matched
                             + calc_driving_distance(cursor, r_start_node,r_end_node) \
                             + calc_driving_distance(cursor, r_end_node, d_end_node)
            detour_distance = d_new_distance - d_original_distance #detour distance
            # print(detour_distance)
            if detour_distance < best_detour:
                best_match_driver = driver
                best_detour = detour_distance
            print(best_detour)

        # print(best_match_driver)
        if best_match_driver is not None: #Insrting matched trip
            query = """
                    INSERT INTO \"rider_requests\" VALUES (%s, 'SRID=4326;POINT(%s %s)', 'SRID=4326;POINT(%s %s)', \
                     'SRID=4326;POINT(%s %s)','SRID=4326;POINT(%s %s)', %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
            data = (trip_id, float(start_location_long), float(start_location_lat), float(end_location_long),
                    float(end_location_lat),float(d_start_long),float(d_start_lat), float(d_end_long), float(d_end_lat),
                    "Matched", float(d_start_long),float(d_start_lat), float(d_end_long), float(d_end_lat),
                    float(start_location_long), float(start_location_lat), float(end_location_long),
                    float(end_location_lat),best_detour)
            # print(query)
            # print(data)
            try:
                cursor.execute(query, data)
            except Exception as e:
                print(e)
                print(e.pgerroe)
            else:
                connection.commit()


    connection.close()





def main():

    sparkContext = SparkContext(appName='rider_stream')
    sparkContext.setLogLevel('ERROR')
    sparkStreamingContext = StreamingContext(sparkContext, 1)
    kafka_params = config('kafka')
    # create DStream that reads from kafka topic
    kafkaStream = KafkaUtils.createDirectStream(sparkStreamingContext, [kafka_params['rider_topic']],
                                                {'metadata.broker.list': kafka_params['broker']})
    # parse the row into separate components
    rider_data_stream = kafkaStream.map(lambda line: line[1].split(";"))

    # rider_data_stream.pprint()

    rider_data_stream.foreachRDD(lambda rdd: rdd.foreachPartition(process_rider_messages))

    sparkStreamingContext.start()
    sparkStreamingContext.awaitTermination()


if __name__ == '__main__':
        main()