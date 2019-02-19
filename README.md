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
## Data Pipeline

![alt text](https://github.com/sivakreddy/Realtime-Ride-Sharing/blob/master/Screen%20Shot%202019-02-19%20at%208.37.33%20AM.png)

#### Data Ingestion

* NYC taxi dataset is in S3. I am using this data to simulate moving drivers and rider requests. I am generating location stream using python, Kafka. 

#### Data Processing

* Spark Stream will process the incoming stream and store data to PostgreSQL. Spark will store driver location data to PostgreSQL and process rider requests to match with nearest driver using PostGIS and PGRouting.

#### Data Storage

* Data is stored into PostgreSQL database, it also user extensions PostGIS and PGrouting extensions. 

#### User INterface

* UI is developed in Flask to display matched trips. It user google api to display the location and routes in UI.

#### Teck stack

* S3, Python, Kafka, Spark-Streaming, PostgreSQL


## Engineering Challenge

* Maps data Preperation: I used osmosis and osm2pgrouting for slicing and loading maps data into PostgreSQL
* Driving distance calculation: I used dijkstra algorithm to minimise cost on the edge to get least driving distance
```
                SELECT sum(cost) FROM pgr_dijkstra(
                'SELECT gid AS id,
                     source,
                     target,
                     cost_s AS cost,
                    FROM ways',
                %s,%s, directed := true);
```

* Matching Algorithm: Driver is matched based on least detour distance.
* Processing huge data: NYC taxi dataset has 1.1 Billion trips. Data issues were explained in a section above.


## UI Output

User interface show matched trips in google maps real-time.

![alt text](https://github.com/sivakreddy/Realtime-Ride-Sharing/blob/master/Screen%20Shot%202019-02-18%20at%207.44.09%20PM.png)

## Further Enhancements

* Ability to match multiple riders with a driver
* Moving data to PostgresXL for data warehousing.
* Mobile app for Driver and Rider
