import random
from datetime import datetime
from kafka.producer import KafkaProducer
import boto3
from smart_open import smart_open
import numpy
from configparser import ConfigParser


#method to read config file
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
    dataset_params = config('dataset')
    producer = KafkaProducer(bootstrap_servers=kafka_params['broker'])

    for obj in bucket.objects.all():
        key = obj.key
        if dataset_params['rider'] not in key:
            continue
        # building absolute file name
        file_name = 's3://nyc-tlc/' + key
        ##skipping header
        firstline = True

        #processing the file
        for line in smart_open(file_name):

            print(line.decode('utf8'))
            if firstline:  # skip first line
                firstline = False
                continue


            line_split = line.decode('utf8').split(",")
            print(line_split)
            if len(line_split) < 20: #skipping rows with huge number of columns
                continue
            if line_split[5] == '0' or line_split[6] == '0' or line_split[7] == '0' or line_split[8] == '0':
                continue
            else:
                start_point = (float(line_split[5]),float(line_split[6]))
                end_point = (float(line_split[7]), float(line_split[8]))
                print(start_point, end_point)

                trip_id =  'ride:' + str(datetime.now()) + ":" + str(random.randint(1, 1000))
                #formatting the message
                str_fmt = "{};{};{};{};{};{}"
                message_info = str_fmt.format(trip_id,
                                              start_point[0],
                                              start_point[1],
                                              end_point[0],
                                              end_point[1],
                                              "In Progress"
                                              )

                print(message_info)
                producer.send(kafka_params['rider_topic'], message_info.encode('utf8 '))



if __name__ == '__main__':
        main()