from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import psycopg2
from configparser import ConfigParser

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

def process_driver_messages(rdd):
    connection = build_postgres_connection()
    cursor = connection.cursor()
    for line in rdd:
        trip_id, start_location_long, start_location_lat,current_location_long, current_location_lat, \
            end_location_long, end_location_lat, status = line[:]

        if status == 'New':
            query = "INSERT INTO \"driver_location\" VALUES (%s, 'SRID=4326;POINT(%s %s)', \
            'SRID=4326;POINT(%s %s)', %s, 'SRID=4326;POINT(%s %s)',%s,%s,%s,%s)"
            # current_location_OSM = "'SRID=4326;POINT(longitude latitude)'"
            data = (trip_id, float(current_location_long), float(current_location_lat), float(end_location_long),
                    float(end_location_lat), status, float(start_location_long), float(start_location_lat),
                    float(start_location_long), float(start_location_lat), float(end_location_long),
                    float(end_location_lat))
            cursor.execute(query, data)
        elif status == 'Done':
            query = "UPDATE \"driver_location\" SET status =  %s \
            where trip_id = %s"

            data = (status, trip_id)
            cursor.execute(query, data)
        else:
            query = "UPDATE \"driver_location\" SET driver_location =  'SRID=4326;POINT(%s %s)', \
            status = %s where trip_id = %s"
            data = (float(current_location_long), float(current_location_lat),status, trip_id)
            cursor.execute(query, data)

    connection.commit()
    connection.close()


def main():

    sparkContext = SparkContext(appName='driver_stream')
    sparkContext.setLogLevel('ERROR')
    sparkStreamingContext = StreamingContext(sparkContext, 1)
    kafka_params = config('kafka')
    # create DStream that reads from kafka topic
    kafkaStream = KafkaUtils.createDirectStream(sparkStreamingContext, [kafka_params['driver_topic']],
                                                {'metadata.broker.list': kafka_params['broker']})
    # parse the row into separate components
    driver_data_stream = kafkaStream.map(lambda line: line[1].split(";"))

    driver_data_stream.pprint()

    driver_data_stream.foreachRDD(lambda rdd: rdd.foreachPartition(process_driver_messages))

    sparkStreamingContext.start()
    sparkStreamingContext.awaitTermination()


if __name__ == '__main__':
        main()