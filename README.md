# Realtime-Ride-Sharing
Location BAsed Realtime Ride Matching Platform

## Business Value

Lot of people commute everyday, but only a small percentage of them car pool. 
Two top reasons that are keeping commuters away from car pooling.

1. Hassle of planning
2. Changes in schedule.

This platform will elimite these two concerns by matching at real time. There by making car pooling more pleasent. 

## Data

NYC Dataset has co-ordinates of source and destination. 


https://console.cloud.google.com/bigquery?supportedpurview=project&angularJsUrl=%2Fprojectselector%2Fbigquery%3Fp%3Dbigquery-public-data%26d%3Dnew_york_taxi_trips%26page%3Ddataset%26supportedpurview%3Dproject&creatingProject&project=my-project-ride-sharing&p=bigquery-public-data&d=new_york_taxi_trips&t=tlc_yellow_trips_2018&page=table

### Schema

vendor_id	STRING	NULLABLE	
A designation for the technology vendor that provided the record.
CMT=Creative Mobile Technologies
VTS= VeriFone, Inc.
DDS=Digital Dispatch Systems
pickup_datetime	TIMESTAMP	NULLABLE	
The date and time when the meter was engaged.
dropoff_datetime	TIMESTAMP	NULLABLE	
The date and time when the meter was disengaged.
pickup_longitude	FLOAT	NULLABLE	
Longitude where the meter was engaged.
pickup_latitude	FLOAT	NULLABLE	
Latitude where the meter was engaged.
dropoff_longitude	FLOAT	NULLABLE	
Longitude where the meter was disengaged.
dropoff_latitude	FLOAT	NULLABLE	
Latitude where the meter was disengaged.
rate_code	STRING	NULLABLE	
The final rate code in effect at the end of the trip.
1= Standard rate
2=JFK
3=Newark
4=Nassau or Westchester
5=Negotiated fare
6=Group ride
passenger_count	INTEGER	NULLABLE	
The number of passengers in the vehicle.  

This is a driver-entered value.
trip_distance	FLOAT	NULLABLE	
The elapsed trip distance in miles reported by the taximeter.
payment_type	STRING	NULLABLE	
A numeric code signifying how the passenger paid for the trip. 
CRD= Credit card
CSH= Cash
NOC= No charge
DIS= Dispute
UNK= Unknown
fare_amount	FLOAT	NULLABLE	
The time-and-distance fare calculated by the meter.
extra	FLOAT	NULLABLE	
Miscellaneous extras and surcharges.  Currently, this only includes the $0.50 and $1 rush hour and overnight charges.
mta_tax	FLOAT	NULLABLE	
$0.50 MTA tax that is automatically triggered based on the metered rate in use.
imp_surcharge	FLOAT	NULLABLE	
$0.30 improvement surcharge assessed on trips at the flag drop. The improvement surcharge began being levied in 2015.
tip_amount	FLOAT	NULLABLE	
Tip amount – This field is automatically populated for credit card tips. Cash tips are not included.
tolls_amount	FLOAT	NULLABLE	
Total amount of all tolls paid in trip.
total_amount	FLOAT	NULLABLE	
The total amount charged to passengers. Does not include cash tips.
store_and_fwd_flag	STRING	NULLABLE	
This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka “store and forward,” because the vehicle did not have a connection to the server. 
Y= store and forward trip
N= not a store and forward trip



## Tech Stack
S3, Python, Spark, Kafka/Pulsar, Redshift, Spark-Streaming, MySQL


## Engineering Challenge

Data Preperation
Realtime streaming.
Matching Algorithm
Analytics on huge data generated.


## MVP

Streaming data, matching algorithm and matched data.
