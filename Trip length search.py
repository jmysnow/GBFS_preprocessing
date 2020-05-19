#!/usr/bin/env python
# coding: utf-8

# # Bikesharing Trip Length Search Tool  
# 
# **Author**: Mengying Ju  
# **Date**: April 11, 2020
# 
# ---
# 
# ATTENTION:
# * Keep the .py file in the same folder of your datafile 
# * Make sure you have packages to be imported in this script installed (*pandas*, *numpy*, *matplotlib*, [**osmnx**](https://pypi.org/project/osmnx/), [**networkx**](https://pypi.org/project/networkx/), **geopandas**, *shapely*...)
# * [Open Street Map](https://www.openstreetmap.org/) is used to extract the road network. Make sure you check your interest area is correct before proceeding.
# * Important parameters are to be set in the cell below.
# 

# In[1]:


# The city name you want to do analysis on
# Make sure the city exists in your generated “Datafiles by city” folder as "<city name>.csv"
# For example, 'San Francisco.csv'
cityname = 'San Francisco' 

# It's the same city of which you want to extract the street network
# This time, add the State name and country name just in case the osmnx takes you to the wrong place
# For example, 'San Francisco' is better to be put as 'San Francisco, California, United States'
# Check whether you've put in the right name by browsing to https://www.openstreetmap.org/.
# Put in name and see whether the first search result is the place you want
place_query = {'city':'San Francisco', 'state':'California', 'country':'USA'}

# Your Google API key
apikey = "yourkey" # Replace the string with your own Google API key


# In[2]:


import pandas as pd
import numpy as np
import osmnx as ox # to extract Open Street Network
import networkx as nx # to help fine shortest path
import geopandas as gpd
# import os
from shapely.geometry import LineString, Point
# from pyproj import CRS
import matplotlib.pyplot as plt

# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"

import warnings
warnings.filterwarnings('ignore')


# In[3]:


'''Load the data in your city'''
trips = pd.read_csv(cityname + '.csv')

'''Delete the rows with Null gps values'''
trips = trips.drop(trips[(trips['Start Latitude'].isnull()) | (trips['Start Longitude'].isnull()) | (trips['End Latitude'].isnull()) | (trips['End Longitude'].isnull())].index)

# '''Delete the rows with GPS out of range'''
# trips = trips.drop(trips[(trips['Start Latitude'] > 46) | (trips['Start Latitude'] < 36)].index)

'''Save the modified data'''
trips.to_csv(cityname + '_modified.csv')


# In[4]:


''' Extract the biking road network from OpenStreetMap '''
graph = ox.graph_from_place(place_query, network_type='all')
ox.plot_graph(graph)

# add elevation to each of the nodes, using the google elevation API, then calculate edge grades
graph = ox.add_node_elevations(graph, api_key=apikey)
graph = ox.add_edge_grades(graph)

''' Convert the network into nodes geodataframe and edges geodataframe respectively '''
nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)


# In[5]:


''' Convert into UTM format ''' 
graph_proj = ox.project_graph(graph)

# get one color for each node, by elevation, then plot the network
nc = ox.get_node_colors_by_attr(graph_proj, 'elevation', cmap='viridis', num_bins=20)
fig, ax = ox.plot_graph(graph_proj, node_color = nc, node_zorder=2)
plt.tight_layout()


''' Convert the projected network into nodes geodataframe and edges geodataframe respectively '''
nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)


# In[6]:


# Find the elevation rises by multiplying edge length together with grade / slope
for u, v, k, data in graph_proj.edges(keys=True, data=True):
    data['rise'] = data['length'] * data['grade']


# In[7]:


'''Get the convex hull of the whole network system'''
# region = edges.unary_union.convex_hull
region_proj = edges_proj.unary_union.convex_hull
region_proj


# In[8]:


'''Create geodataframes for Origins and Destinations'''
''' Start points'''
starts = gpd.GeoDataFrame(trips, geometry = gpd.points_from_xy(trips['Start Longitude'], trips['Start Latitude']))
starts = starts[['Start Latitude', 'Start Longitude', 'geometry']]

''' End points'''
ends = gpd.GeoDataFrame(trips, geometry = gpd.points_from_xy(trips['End Longitude'], trips['End Latitude']))
ends = ends[['End Latitude', 'End Longitude', 'geometry']]


# In[12]:


'''Make sure the coordinate systems are consistent with the road network'''
starts.crs = edges.crs
ends.crs = edges.crs


# In[13]:


'''Convert the Origin and Destination geodataframes into the projected coordinate'''
'''So that we could calculate the distances more accurately'''
starts_proj = starts.to_crs(edges_proj.crs)
ends_proj = ends.to_crs(edges_proj.crs)

''' Select the observations where both start and end points are within the city area '''
start_mask = starts_proj.within(region_proj)
end_mask = ends_proj.within(region_proj)
mask = start_mask & end_mask

trips_in = trips.loc[mask]
starts_in = starts_proj.loc[mask]
ends_in = ends_proj.loc[mask]


# In[14]:


# trips_in.shape


# In[ ]:


# ''' Plot the projected data altogether '''
# fig, ax = plt.subplots(figsize = (16, 8))
# starts_proj.plot(ax = ax)
# ends_proj.plot(ax = ax, color = 'pink', markersize = 2, alpha = 0.3)

# starts_in.plot(ax = ax, color = 'blue', markersize = 2, alpha = 0.3)
# ends_in.plot(ax = ax, color = 'purple', markersize = 2, alpha = 0.3)
# plt.title("Trip starts and ends (projected within)")


# In[15]:


''' Only plot the data in your interest area '''
fig, ax = plt.subplots(figsize = (16, 8))

starts_in.plot(ax = ax, color = 'blue', markersize = 2, alpha = 0.3)
ends_in.plot(ax = ax, color = 'purple', markersize = 2, alpha = 0.3)
plt.title("Trip starts and ends (projected zoom)")


# In[16]:


''' Name all the geometry shapes of the origin and destination points '''
orig_points = list(starts_in.geometry)
target_points = list(ends_in.geometry)


# In[16]:


''' Put the XY information into the origin / target XY list'''
orig_xy = [(o.y, o.x) for o in orig_points]
target_xy = [(t.y, t.x) for t in target_points]


''' Find the nearest nodes for each origin and each target in the road network'''
orig_nodes = []
for i in range(len(trips_in)): # use len(trips_in) instead when dealing with the whole dataset
    orig_nodes.append(ox.get_nearest_node(graph_proj, orig_xy[i], method='euclidean'))
    print(i)
    
target_nodes = []
for i in range(len(trips_in)): # use len(trips_in) instead when dealing with the whole dataset
    target_nodes.append(ox.get_nearest_node(graph_proj, target_xy[i], method='euclidean'))
    print(i)

''' Locate the rows for the closest origins and targets separately'''
o_closest = nodes_proj.loc[orig_nodes]
t_closest = nodes_proj.loc[target_nodes]


# In[19]:


''' Find the routes for all od pairs '''
routes = []
for i in range(len(orig_nodes)):
    try:
        routes.append(nx.shortest_path(G = graph_proj, source = orig_nodes[i], target = target_nodes[i], weight = 'length'))
    except:
        routes.append(np.NaN)
    print(i)


# In[20]:


''' Replace the nans with straighlines, and replace the routes with only one node with two same nodes'''
routes = pd.Series(routes)
null_index = routes[routes.isnull()].index


# In[22]:


for i in range(len(routes)):
    if i in null_index or len(routes[i]) == 1:
        routes[i] = [orig_nodes[i], target_nodes[i]]


# In[48]:


''' Create a geodataframe to store all the results'''
''' Including all the elevation information '''
route_geom = gpd.GeoDataFrame(crs=edges_proj.crs)
route_geom['geometry'] = None
route_geom['osmids'] = None

for i in range(len(routes)):
    route_nodes = nodes_proj.loc[routes[i]]
    route_line = LineString(list(route_nodes.geometry.values))
    route_geom.loc[i, 'geometry'] = route_line
    route_geom.loc[i, 'osmids'] = str(list(route_nodes['osmid'].values))
    
    # Get the slope information
    try:
        route_grades = ox.get_route_edge_attributes(graph_proj, routes[i], 'grade_abs')
        route_geom.loc[i, 'avg_grade (%)'] = np.mean(route_grades)*100
        route_geom.loc[i, 'max_grade (%)'] = np.max(route_grades)*100
        route_geom.loc[i, 'min_grade (%)'] = np.min(route_grades)*100
    except:
        route_geom.loc[i, 'avg_grade (%)'] = np.NaN
        route_geom.loc[i, 'max_grade (%)'] = np.NaN
        route_geom.loc[i, 'min_grade (%)'] = np.NaN
    
    # Get the rises
    try:
        route_rises = ox.get_route_edge_attributes(graph_proj, routes[i], 'rise')
        ascent = np.sum([rise for rise in route_rises if rise >= 0])
        descent = np.sum([rise for rise in route_rises if rise < 0])
        route_geom.loc[i, 'tol_elevation change (m)'] = np.sum(route_rises)
        route_geom.loc[i, 'elevation_up (m)'] = ascent
        route_geom.loc[i, 'elevation_down (m)'] = abs(descent)
    except:
        route_geom.loc[i, 'tol_elevation change (m)'] = 0
        route_geom.loc[i, 'elevation_up (m)'] = 0
        route_geom.loc[i, 'elevation_down (m)'] = 0
    print(i)  
route_geom['length (m)'] = route_geom.length



# In[53]:


'''Add the trip length attribute at the end'''
# trips_in['length (m)'] = list(route_geom['length_m'])
# trips_in['avg_grade (%)'] = list(route_geom['avg_grade (%)'])
# trips_in['max_grade (%)'] = list(route_geom['max_grade (%)'])
# trips_in['tol_elevation change (m)'] = list(route_geom['tol_elevation change (m)'])
# trips_in['elevation_up (m)'] = list(route_geom['elevation_up (m)'])
# trips_in['elevation_down (m)'] = list(route_geom['elevation_down (m)'])

# trips_2000 = trips_in[:2000].copy()
trips_in['length (m)'] = list(route_geom['length (m)'])
trips_in['avg_grade (%)'] = list(route_geom['avg_grade (%)'])
trips_in['max_grade (%)'] = list(route_geom['max_grade (%)'])
trips_in['min_grade (%)'] = list(route_geom['min_grade (%)'])
trips_in['tol_elevation change (m)'] = list(route_geom['tol_elevation change (m)'])
trips_in['elevation_up (m)'] = list(route_geom['elevation_up (m)'])
trips_in['elevation_down (m)'] = list(route_geom['elevation_down (m)'])
trips_in['geometry'] = list(route_geom['geometry'])

# In[55]:


''' Save the results'''
# trips_in.to_csv(cityname + '_with length.csv')
trips_in.to_csv(cityname + '_with length and elevation.csv')

