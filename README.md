# Realtime-Ride-Sharing
Location Based Realtime Ride Matching Platform

## Business Value

120 Million of people commute everyday in USA, but only a 22% of them car pool. 
Top reason that is keeping commuters away from car pooling.

1. Hassle of planning and co-ordination

This platform will elimite these two concerns by matching at real time. There by, making car pooling more pleasent while saving commute costs by as much as 50%. 

## Data

NYC Dataset has co-ordinates of source and destination. 

https://console.cloud.google.com/bigquery?supportedpurview=project&angularJsUrl=%2Fprojectselector%2Fbigquery%3Fp%3Dbigquery-public-data%26d%3Dnew_york_taxi_trips%26page%3Ddataset%26supportedpurview%3Dproject&creatingProject&project=my-project-ride-sharing&p=bigquery-public-data&d=new_york_taxi_trips&t=tlc_yellow_trips_2018&page=table

### Schema

trips table contains all yellow and green taxi trips. Each trip has a cab_type_id, which references the cab_types table and refers to one of yellow or green
It has foollowing columns for geolocation:

1. pickup_longitude
2. pickup_latitude
3. dropoff_longitude
4. dropoff_latitude




## Tech Stack
S3, Python, Kafka, Spark-Streaming, PostgreSQL


## Engineering Challenge

Data Preperation
Realtime streaming.
Matching Algorithm
Analytics on huge data generated.


## MVP

Streaming data, matching algorithm and matched data.
