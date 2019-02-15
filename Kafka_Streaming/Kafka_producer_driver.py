import random
from datetime import datetime
from kafka.producer import KafkaProducer
import boto3
from smart_open import smart_open
import numpy
from configparser import ConfigParser




def format_message(trip_id, start_location,current_location, end_location, status):
    str_fmt = "{};{};{};{};{};{};{};{}"
    message = str_fmt.format(trip_id,
                             start_location[0],
                             start_location[1],
                             current_location[0],
                             current_location[1],
                             end_location[0],
                             end_location[1],
                             status
                             )
    print(message)
    return message

def getEquidistantPoints(p1, p2, parts):
    return zip(numpy.linspace(p1[0], p2[0], parts+1), numpy.linspace(p1[1], p2[1], parts+1))

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


def main():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('nyc-tlc')
    # Iterates through all the objects, doing the pagination for you. Each obj
    # is an ObjectSummary, so it doesn't contain the body. You'll need to call
    # get to get the whole body.
    kafka_params = config('kafka')
    producer = KafkaProducer(bootstrap_servers=kafka_params['broker'])
    for obj in bucket.objects.all():
        key = obj.key
        # body = obj.get()['Body'].read()
        iterlines = iter(smart_open('s3://nyc-tlc/trip data/green_tripdata_2013-08.csv'))
        next(iterlines)
        firstline = True

        for line in smart_open('s3://nyc-tlc/trip data/green_tripdata_2013-08.csv'):
            # if line.decode('utf8') == '/n/r':
            #     continue
            print(line.decode('utf8'))
            if firstline:  # skip first line
                firstline = False
                continue


            line_split = line.decode('utf8').split(",")
            print(line_split)
            if len(line_split) < 20:
                continue
            if line_split[5] == '0' or line_split[6] == '0' or line_split[7] == '0' or line_split[8] == '0':
                continue
            else:
                start_point = (float(line_split[5]),float(line_split[6]))
                end_point = (float(line_split[7]), float(line_split[8]))
                print(start_point, end_point)
                intermediate_points = getEquidistantPoints(start_point, end_point, 100)
                print(intermediate_points)

                trip_id = 'drive:' + str(datetime.now()) + ":" + str(random.randint(1, 1000))
                formatted_message = format_message(trip_id,
                                                   start_point,
                                                   start_point,
                                                   end_point,
                                                   "New")

                producer.send('driver_location', formatted_message.encode('utf8 '))

                for int_point in intermediate_points:
                    print(int_point)

                    formatted_message = format_message(trip_id,
                                                       start_point,
                                                       int_point,
                                                       end_point,
                                                       "In Progress")

                    producer.send('driver_location', formatted_message.encode('utf8 '))

                formatted_message = format_message(trip_id,
                                                   start_point,
                                                   end_point,
                                                   end_point,
                                                   "Closed")

                producer.send(kafka_params['driver_topic'], formatted_message.encode('utf8 '))



if __name__ == '__main__':
        main()