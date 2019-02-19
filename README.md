# Realtime-Ride-Sharing
Location Based Realtime Ride Matching Platform

## Business Value

120 Million of people commute everyday in USA, but only a 22% of them car pool. 
Top reason that is keeping commuters away from car pooling.

1. Hassle of planning and co-ordination

This platform will elimite these two concerns by matching at real time. There by, making car pooling more pleasent while saving commute costs by as much as 50%. 

## Data

I used primarily two datasets.

[NYC taxi Dataset](https://registry.opendata.aws/nyc-tlc-trip-records-pds/)

[OSM Dataset](http://download.geofabrik.de/north-america.html)


### Schema

trips table contains all yellow and green taxi trips. Each trip has a `cab_type_id`, which references the `cab_types` table and refers to one of yellow or green. 
It has foollowing columns for geolocation:

1. `pickup_longitude`
2. `pickup_latitude`
3. `dropoff_longitude`
4. `dropoff_latitude`

`taxi_zones` table contains the TLC's official taxi zone boundaries. Starting in July 2016, the TLC no longer provides pickup and dropoff coordinates. Instead, each trip comes with taxi zone pickup and dropoff location IDs

### Data issues

#### NYC taxi data
* Remove carriage returns and empty lines from TLC data. 
* Some raw data files have extra columns with empty data, had to create dummy columns junk1 and junk2 to absorb them
* Two of the yellow taxi raw data files had a small number of rows containing extra columns. I discarded these rows
* The official NYC neighborhood tabulation areas (NTAs) included in the census tracts shapefile are not exactly what I would have expected. Some of them are bizarrely large and contain more than one neighborhood, e.g. "Hudson Yards-Chelsea-Flat Iron-Union Square", while others are confusingly named, e.g. "North Side-South Side" for what I'd call "Williamsburg", and "Williamsburg" for what I'd call "South Williamsburg". In a few instances I modified NTA names, but I kept the NTA geographic definitions

#### OSM data
* OSM data is very large, so I downloaded it only for states NY, NJ,CT. Again I need maps only for NYC area. So, I used `osmosis` to select maps data within specific boundaries

```
osmosis \
  --read-xml new-jersey-latest.osm --tee 1 \
  --bounding-box left=-74.584213\
 top=41.189624 \
 bottom=40.472283 \
 right=-71.757647 \
--write-xml NYC-box-NJ.osm
```
* Each state data is too large to load into Postgres. So I had to split them into multiple small files
```
osmosis \
  --read-xml NYC-box-NJ --tee 4 \
  --bounding-box left=-74.543049\
 top=40.611474 \
 --write-xml new-jersey-SE.osm \
  --bounding-box left=-74.543049 \
 bottom=40.611474 \
 --write-xml new-jersey-NE.osm \
  --bounding-box right=-74.543049 \
 top=40.611474 \
 --write-xml new-jersey-SW.osm \
  --bounding-box right=-74.543049 \
 bottom=40.611474 \
 --write-xml new-jersey-NW.osm
```
## Tech Stack
S3, Python, Kafka, Spark-Streaming, PostgreSQL


## Engineering Challenge

Data Preperation
Realtime streaming.
Matching Algorithm
Analytics on huge data generated.


## MVP

Streaming data, matching algorithm and matched data.
