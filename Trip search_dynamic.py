#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Mengying Ju 
# April 11, 2020

''' 
ATTENTION:
1. Keep the .py file in the same folder of your datafile 
2. Make sure the datafile comes without headers, otherwise comment out line 114
3. Make sure your have packages to be imported in this script installed (pandas, numpy, matplotlib, pytz, gmaps, requests, json, os...)
4. Make sure you have an Google API key and have activated "Timezone" and "Geocode" API in your Google Cloud Console. 
https://console.cloud.google.com/
5. Important parameters are to be set here.
'''
filename = "trips 02 28 2020.csv" # Replace the string with your own csv file name
apikey = "yourkey" # Replace the string with your own Google API key


# In[1]:


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import pytz
import gmaps
import requests
import json
import os
import time
import warnings
warnings.filterwarnings('ignore')

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


# ## Create a class script to convert TIMEZONES and CITY locations
# #### --> Google map api key required

# In[2]:


# Create a class to search for timezones
class GoogleLocation(object):
    def __init__(self, api_key):
        super(GoogleLocation, self).__init__()
        self.api_key = api_key
        self.TZurl = "https://maps.googleapis.com/maps/api/timezone/json"
        self.CTurl = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # define a method to search for timezones
    def search_timezone(self, lat, lon, timestamp):
        params = {
            'location': str(lat) + ',' + str(lon),
            'timestamp': str(timestamp),
            'key': self.api_key
        }
        res = requests.get(self.TZurl, params = params)
        results = json.loads(res.content)
        if results:
            return results['timeZoneId'], results['timeZoneName']
        else:
            return np.NaN, np.NaN
    
    # define a method to search for the city name
    def search_city(self, lat, lon):
        params = {
            'latlng': str(lat) + ',' + str(lon),
            'key': self.api_key
        }
        res = requests.get(self.CTurl, params = params)
        if json.loads(res.content)['results']:
            results = json.loads(res.content)['results'][0]['address_components']
           
            city_name, county_name, state_name, country_name = "", "", "", ""
            for i in range(len(results)):
                if 'sublocality' in results[i]['types']:
                    county_name = results[i]['long_name']
                elif 'locality' in results[i]['types']:
                    city_name = results[i]['long_name']
                elif 'administrative_area_level_1' in results[i]['types']:
                    state_name = results[i]['long_name']
                elif 'country' in results[i]['types']:
                    country_name = results[i]['long_name']
            if city_name == '':
                if county_name == '':
                    return state_name, country_name
                return county_name, country_name
            return city_name, country_name
        else:
            return np.NaN, np.NaN


# ## Create a class that inherits from the search class, which reads datafiles and does analysis

# In[4]:


# Initialize a class to read the dynamic data
# It splits the data into different operators (and different cities), and automatically save the results into a folder
class PreProcessing(object):
    # Initialization
    def __init__(self, filename, api):
        '''
        filename is the directory of the data file
        '''
        self.trips = pd.read_csv(filename)
        
        self.add_header() # Only add this line if the header is missing
        
        # Drop the NaN operators
        self.trips = self.trips.drop(self.trips[self.trips['Operator'].isnull()].index)
        self.trips.index = range(len(self.trips))
        
        # Convert time from unix to utc
        self.trips['Start datetime (UTC)'] = pd.to_datetime(self.trips['Start time'], unit = 's')
        self.trips['End datetime (UTC)'] = pd.to_datetime(self.trips['End time'], unit = 's')
        
        self.api_search = GoogleLocation(api)      
#         self.add_provider() # To get general providers        
#         self.providers = pd.unique(self.trips['Provider'])
        self.add_city()
    
        # Drop the NaN cities
        self.trips = self.trips.drop(self.trips[self.trips['city'].isnull()].index)
        self.trips.index = range(len(self.trips))

        self.add_timezone()
        
        # Convert from UTC to timezone
        self.trips['Start datetime (local)'] = self.trips.apply(lambda x: pytz.timezone('Etc/UTC').localize(x['Start datetime (UTC)']).astimezone(x['timezone']), axis = 1)
        self.trips['End datetime (local)'] = self.trips.apply(lambda x: pytz.timezone('Etc/UTC').localize(x['End datetime (UTC)']).astimezone(x['timezone']), axis = 1)

 
    
    
    # Print the first few lines
    def view(self, lines = 5):
        return self.trips.head(lines)
    
    # Return the whole dataframe
    def view_all(self):
        return self.trips
        
    # Run this method if the header is missing
    def add_header(self):
        first_row = list(self.trips.columns)
        
        # Define the first row
        new_header = ['Operator', 'Bike ID', 'Reservation Time', 'Start time', 'Start Latitude', 'Start Longitude', 
                                  'End time', 'End Latitude', 'End Longitude', 'Charge % start', 'Charge % End']
        # Add the original header line into the first line
        temp_dic = dict()
        temp_rename = dict()
        for i in range(len(new_header)):
            temp_dic[new_header[i]] = [first_row[i]]
            temp_rename[first_row[i]] = new_header[i]
        temp_dic = pd.DataFrame(temp_dic)
        self.trips = self.trips.rename(columns = temp_rename)
        
        # Append the two dataframes together to get a combined one
        self.trips = pd.concat([temp_dic, self.trips], ignore_index = True)
        
    # Use google api search to store which city and country it belongs to
    def add_city(self):
        
        self.trips['city'], self.trips['country'] = np.NaN, np.NaN

        i = 0
        operators = pd.unique(self.trips['Operator'])
        for op in operators:
            op_data = self.trips[self.trips['Operator'] == op].reset_index()
#             time.sleep(2) # To avoid speed limit!!
            city, country = self.api_search.search_city(float(op_data.loc[0, 'Start Latitude']), float(op_data.loc[0, 'Start Longitude']))
            self.trips.loc[self.trips['Operator'] == op, 'city'] = city
            self.trips.loc[self.trips['Operator'] == op, 'country'] = country
            print(i) # For you to keep track of verbose iterations
            i += 1

            
    def add_timezone(self):
        self.trips['timezone'], self.trips['timezoneID'] = np.NaN, np.NaN
        
        i = 0
        cities = pd.unique(self.trips['city'])
        for ct in cities:
            ct_data = self.trips[self.trips['city'] == ct].reset_index()
#             time.sleep(2) # To avoid speed limit!!
            timezone, timezoneID = self.api_search.search_timezone(float(ct_data.loc[0, 'Start Latitude']), 
                                                               float(ct_data.loc[0, 'Start Longitude']),
                                                               ct_data.loc[0, 'Start time'])
            self.trips.loc[self.trips['city'] == ct, 'timezone'] = timezone
            self.trips.loc[self.trips['city'] == ct, 'timezoneID'] = timezoneID
            print(i) # For you to keep track of verbose iterations
            i += 1
        

            
    # Add provider information (only works for now)
    # Cannot take newly added providers into account
    # The method takes long
    def add_provider(self, new_providers = []):
        
        # Can modify this list
        providers = ['lyft', 'jump', 'spin', 'nextbike', 'breeze',
                     'bishop', 'bcycle', 'movo', 'relay', 'sobi',
                     'grid', 'lime', 'beryl', 'boise', 'topeka',
                     'CKL', 'BOLT', 'reddy', 'university_of_virginia',
                     'BA', 'coast', 'bird', 'biketown']
        providers = providers + new_providers
        
        self.trips['Provider'] = np.NaN
        
        for p in providers:
            self.trips.loc[self.trips['Operator'].str.contains(p), 'Provider'] = p
            
        # For the rest of unknown operators, jut put the name of Operator to Provider
        self.trips.loc[self.trips['Provider'].isnull(), 'Provider'] = self.trips.loc[self.trips['Provider'].isnull(), 'Operator']
    
    # Split the data by operator, and save them all
    def split_operator(self):
        
        # Create a new folder to store all the operator files
        if not os.path.exists('Datafiles by operator'):
            os.mkdir('Datafiles by operator')
            
        operators = pd.unique(self.trips['Operator'])     
        for op in operators:
            op_data = self.trips[self.trips['Operator'] == op]
            op_data.index = range(len(op_data))
            op_data.to_csv(os.path.join("Datafiles by operator", op + ".csv"))
            print(op) # For you to keep track of verbose iterations
    
    # Split the data by city, and save them all
    def split_city(self):
        
        # Create a new folder to store all the operator files
        if not os.path.exists('Datafiles by city'):
            os.mkdir('Datafiles by city')
            
        cities = pd.unique(self.trips['city'])
        for ct in cities:
            ct_data = self.trips[self.trips['city'] == ct]
            ct_data.index = range(len(ct_data))
            ct_data.to_csv(os.path.join("Datafiles by city", ct + ".csv"))
            print(ct) # For you to keep track of verbose iterations


# In[1]:


# Initialize an object to do all the work
file_reader = PreProcessing(filename, apikey) 
file_reader.split_operator()
file_reader.split_city()


# In[ ]:
