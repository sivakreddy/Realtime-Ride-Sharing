import random
import sys
from datetime import datetime
from kafka.producer import KafkaProducer
from kafka.client import KafkaClient
import boto3
import pandas as pd
from smart_open import smart_open
import numpy

# producer = KafkaProducer(bootstrap_servers= 'ec2-52-32-41-146.us-west-2.compute.amazonaws.com:9092')
# client = boto3.client('s3')
# resource = boto3.resource('s3')
# my_bucket = resource.Bucket('nyc-tlc')
# obj = client.get_object(Bucket='nyc-tlc', Key='/trip\ data/yellow_tripdata_2018-06.csv')
# trips = pd.read_csv(obj['Body'])

s3 = boto3.resource('s3')
bucket = s3.Bucket('nyc-tlc')
# Iterates through all the objects, doing the pagination for you. Each obj
# is an ObjectSummary, so it doesn't contain the body. You'll need to call
# get to get the whole body.
def getEquidistantPoints(p1, p2, parts):
    return zip(numpy.linspace(p1[0], p2[0], parts+1), numpy.linspace(p1[1], p2[1], parts+1))

producer = KafkaProducer(bootstrap_servers= 'ec2-52-32-41-146.us-west-2.compute.amazonaws.com:9092')
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

            trip_id =  str(datetime.now()) + ":" + str(random.randint(1, 1000))


            for int_point in intermediate_points:
                print(int_point)

                str_fmt = "{};{};{};{};{};{}"
                message_info = str_fmt.format(trip_id,
                                              start_point[0],
                                              start_point[1],
                                              end_point[0],
                                              end_point[1],
                                              "In Progress"
                                              )

                print(message_info)
                producer.send('driver_location', message_info.encode('utf8'))


        #
# class Producer(object):
#
#     def __init__(self):
#         self.producer = KafkaProducer(bootstrap_servers= 'ec2-52-32-41-146.us-west-2.compute.amazonaws.com:9092')
#         self.client = boto3.client('s3')
#         self.resource = boto3.resource('s3')
#         self.my_bucket = self.resource.Bucket('nyc-tlc')
#
#     def produce_msgs(self):
#         obj = self.client.get_object(Bucket='my-bucket', Key='/trip\ data/yellow_tripdata_2018-06.csv')
#         trips = pd.read_csv(obj['Body'])
#
#         msg_cnt = 0
#         for trip in trips:
#             time_field = datetime.now().strftime("%Y%m%d %H%M%S")
#             str_fmt = "{};{};{};{}"
#             message_info = str_fmt.format('yellow',
#                                           time_field,
#                                           price_field,
#                                           volume_field)
# #            print message_info
#             self.producer.send('price_data_part4', message_info)
#             msg_cnt += 1
#
# if __name__ == "__main__":
#     # args = sys.argv
#     # ip_addr = str(args[1])
#     # partition_key = str(args[2])
#     prod = Producer()
#     prod.produce_msgs()