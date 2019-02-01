from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SQLContext
import psycopg2

def main():

    sparkContext = SparkContext(appName='driver_stream')
    sparkContext.setLogLevel('ERROR')
    sparkStreamingContext = StreamingContext(sparkContext, 1)
    # create DStream that reads from kafka topic
    kafkaStream = KafkaUtils.createDirectStream(sparkStreamingContext, ['driver_location'],
                                                {'metadata.broker.list': 'ec2-52-32-41-146.us-west-2.compute.amazonaws.com:9092'})
    # parse the row into separate components
    driver_data_stream = kafkaStream.map(lambda line: line[1].split(";"))

    driver_data_stream.pprint()


if __name__ == '__main__':
        main()