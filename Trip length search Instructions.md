# *Trip length search* Instructions
*<p style="text-align: center;"> 
The following instructions are for ```Trip length search.py```</p>*
*<p style="text-align: center;">     
Run the script only after running ```Trip search_dynamic.py```</p>*
*<p style="text-align: center;">   
    The script works for [Python 3](https://www.python.org/downloads/) and is used to find the trip distances offline </p>*
    
###### <p style="text-align: right;"> Mengying Ju </p>
###### <p style="text-align: right;"> May 19, 2020 </p>


## Introduction

> To find the trip distances from a given origin/destination pair, [Google Maps](https://www.google.com/maps) does a great job in telling us how far it is and how long it takes. However, it is not feasible to use API when the number of queries is huge.
> 
> An offline approach using the shortest path algorithm is therefore developed to avoid [```OVER_QUERY_LIMIT```](https://developers.google.com/maps/premium/previous-licenses/articles/usage-limits).

This script can - 
* Extract the road network in your interest area from [OpenStreetMap](https://www.openstreetmap.org/).
* Filter the trips with both origins and destinations inside your interest area.
* Find the shortest path for each OD pair in your filtered trips
* Find the trip distance of each OD pair, according to the shortest paths
* Save the distances and paths in a new .csv file.

## Attentions
Here are the things to pay attention to before you get started.
-	Keep the .py file in the **same folder** of your datafile
-	The script only works for the trips with both origins and destinations inside your interest city.
-	Make sure you have activated “[Elevation](https://developers.google.com/maps/documentation/elevation/start)” API in your [Google Cloud Console](https://console.cloud.google.com/).
-	Make sure you have packages to be imported in this script installed ([pandas](https://pypi.org/project/pandas/), [numpy](https://pypi.org/project/numpy/), [matplotlib](https://pypi.org/project/matplotlib/), osmnx, networkx, geopandas, and shapely). Below is a brief introduction of how the important packages work.
    * **[osmnx](https://pypi.org/project/osmnx/)**: To extract [OpenStreetMap](https://www.openstreetmap.org/) network
    * **[networkx](https://pypi.org/project/networkx/)**: To help find the shortest path
    * **[geopandas](https://pypi.org/project/geopandas/)**: To store great amount of shape objects into data frames
    * **[shapely](https://pypi.org/project/Shapely/)**: To work with shapefiles in Python 3
-	Set the ```cityname```, ```place_query``` and ```apikey``` in *[line 24](https://github.com/jmysnow/GBFS_preprocessing/blob/87043a6a3e110509e9d683b342d8a5de14263bd2/Trip%20length%20search.py#L24)*, *[line 31](https://github.com/jmysnow/GBFS_preprocessing/blob/87043a6a3e110509e9d683b342d8a5de14263bd2/Trip%20length%20search.py#L31)* and *[line 34](https://github.com/jmysnow/GBFS_preprocessing/blob/87043a6a3e110509e9d683b342d8a5de14263bd2/Trip%20length%20search.py#L34)*.
    -	**cityname**:
        -	The name of the city that you want to do analysis on
        - Make sure the city exists in your generated “Datafiles by city” folder as "<city name>.csv". For example, 'San Francisco.csv'
    -	**place_query**:
        -	It’s the same city of which you want to extract the street network
        -	Add the State name and country name just in case the osmnx takes you to the wrong place
        -	For example, 'San Francisco' is better to be put as 'San Francisco, California, United States'.
        -	It's formatted as a dictionary: ```{'city':'San Francisco', 'state':'California', 'country':'USA'}```, so all you have to do is to replace the values to ```city```, ```state``` and ```country``` to suffice your own need.
        -	Check whether you've put in the right name by browsing to https://www.openstreetmap.org. Put in the name and see whether the first search result is the place you want.

    -	**apikey**: Your Google API key.
    
If everything goes as expected, it will generate two files: ```<city name>_modified.csv``` and ```<city name>_with length and elevation.csv``` in your folder.
    

## Functionalities and logic
The script works in the following logic:
1.	Obtain the road network from [OpenStreetMap](https://www.openstreetmap.org/)
2.  Add the *length* and *elevation* attributes to the network.
3.	Drop the rows with ```N/A``` latitude / longitude because there’s no way to know where they are.
4.	Save the fixed datafile as ```<city name>_modified.csv``` in your folder.
5.	Filter out the trip with both origins and destinations falling into your interest area.
6.	Find the nearest network node for each origin and destination.
7.	Find the shortest path (represented with a list of node indexes) for each approximated OD pairs.
8.	Compose each path into *LineStrings* and find the lengths and elevation changes.
9.	Add the *length* and *elevation* attribute to the original trip data.
    To put it in another way, 8 additional fields will be added to the original data:
    * **length (m)**: The trip distance in meters.
    * **avg_grade (%)**: The grade $\frac{height (m)}{length (m)}$ averaged over all edges in a given route.
    * **max_grade (%)**: The greatest grade, or slope, across all edges in a given route.
    * **min_grade (%)**: The smallest grade, or slope, across all edges in a given route.
    * **elevation_up (m)**: *Elevation change* if it's positive.
    * **elevation_down (m)**: *Negative elevation change* if it's negative.
    * **tol_elevation change (m)**: ```elevation_up (m) - elevation_down (m)```
    * **geometry**: The *LineString* of the shortest route.
10.	Save the data with shortest path distances as ```<city name>_with length and elevation.csv``` in your folder.


## Steps to follow
After making the changes stated in part I, simply run the whole file. The file with trip distances calculated will show up when they’re done.





