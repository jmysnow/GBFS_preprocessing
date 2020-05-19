# *Trip search_dynamic* Instructions

*<p style="text-align: center;"> 
The following instructions are for ```Trip search_dynamic.py``` </p>*
*<p style="text-align: center;">  The script works for [Python 3](https://www.python.org/downloads/) and is used for **MDS** data preprocessing </p>*
    
    
###### <p style="text-align: right;"> Mengying Ju </p>
###### <p style="text-align: right;"> May 19, 2020 </p>



## Introduction

> Bikesharing systems post information on [GBFS (General Bikeshare Feed Specification)](https://github.com/NABSA/gbfs) feeds.  This information when appropriately organized has trip data. The problem is that the timestamps are in Unix time, which is unusable. 
>
> This script coverts those Unix times into local times.  Furthermore, input files usually have many operators and cities mixed together.  This scripts splits each operator data into separate files.

This script can - 
* Help you add time zones for each trip.
* Convert UTC time to local time.
* Find out in what cities and countries where the trips are taking place.
* Split the master file into small separate files by city and by operator.

 
## Attentions 
- Keep the .py file in the **same folder** of your datafile.
- Make sure the datafile comes without headers, otherwise comment out *[line 114](https://github.com/jmysnow/GBFS_preprocessing/blob/dd43429ea3038f31559f075846f6b41b57616e1a/Trip%20search_dynamic.py#L114)*.
-	Make sure you have packages to be imported in this script installed ([pandas](https://pypi.org/project/pandas/), [numpy](https://pypi.org/project/numpy/), [matplotlib](https://pypi.org/project/matplotlib/), [pytz](https://pypi.org/project/pytz/), [gmaps](https://pypi.org/project/gmaps/), [requests](https://pypi.org/project/requests/), json, os, and time). Below is a brief introduction of how the important packages work.
    * **[pytz](https://pypi.org/project/pytz/)**: To convert UTC time to local time given a specific time zone.
    * **[requests](https://pypi.org/project/requests/)**: To pull json data using Google Maps API.

- Make sure you have an Google API key and have activated "[Timezone](https://developers.google.com/maps/documentation/timezone/start)" and "[Geocode](https://developers.google.com/maps/documentation/geocoding/start)" API in your [Google Cloud Console](https://console.cloud.google.com/). 
- Set the ```filename``` and ```apikey``` in *[line 19](https://github.com/jmysnow/GBFS_preprocessing/blob/dd43429ea3038f31559f075846f6b41b57616e1a/Trip%20search_dynamic.py#L19)* and *[line 20](https://github.com/jmysnow/GBFS_preprocessing/blob/dd43429ea3038f31559f075846f6b41b57616e1a/Trip%20search_dynamic.py#L20)*.
    * The ```filename``` is the name of your .csv file.
    * The ```apikey``` is your Google API key.
- The whole script takes about **20min** to run in a **64-bit 8GB i7** laptop, but it takes shorter in a computer with a bigger memory storage.

## Classes and functionalities
The script includes two classes.
**Preprocessing class** relies on the configuration of **GoogleLocation class** for API searches.

1. **GoogleLocation class** takes an API key, and initializes a search instance:
    * **search_timezone(self, lat, lon, timestamp)** takes a GPS location and a timestamp, and returns the timezone the GPS spot falls in.
    * **search_city(self, lat, lon)** takes a GPS location, and returns the city and the country name that the GPS spot falls in.
2. **Preprocessing class** takes a file name and an API key, and initializes an instance that does all the preprocessing work:
    * **add_header(self)**: The given data file comes without header line, so we need to run this method to append the first line into the whole dataset. If the data comes with its own header, then no need to do so.
    * **add_city(self)**: It adds the city and country information, via API search, assuming all records for a given operator come from the same city.
    * **add_timezone(self)**: It adds the time zone information.
    * **add_provider(self, new_providers = [])**:It generalize the operators into providers. For example, all operator names containing “lyft” as provider Lyft.
    * **split_operator(self)**: Split the data by operator and save them all.
    * **split_city(self)**: Split the data by city and save them all.

## Steps to follow

After making the changes stated in *Attentions*, simply run the whole file. The disaggregated files will show up when they’re done.

