#!/usr/bin/env python
# coding: utf-8

# In[19]:


import pandas as pd
import numpy as np
import datetime
from datetime import *
import time

filename = 'adc_by_time.csv'
adc_by_time = pd.read_csv(filename)
adc_by_time = adc_by_time.drop(columns='Unnamed: 0')

def timeround10(dt):                                               # function to round current time to nearest 10 min
    a, b = divmod(round(dt.minute, -1), 60)
    rounded_time = '%i:%02i' % ((dt.hour + a) % 24, b)
    rounded_time = datetime.strptime(rounded_time,"%H:%M")
    rounded_time = rounded_time.strftime("%H:%M:%S")
    return rounded_time

def get_adc():
    try:
        now = datetime.strptime(str(datetime.now()),"%Y-%m-%d %H:%M:%S.%f")
        month = int(now.strftime("%m"))
        time_striffed = now.strftime("%H:%M:%S")
        time_stripped = datetime.strptime(time_striffed,"%H:%M:%S")
        month_df = adc_by_time.loc[adc_by_time['Month'] == month]
        lookup_time = timeround10(time_stripped)                         # rounds to nearest 10 min
        new_df = month_df.loc[month_df['Time'] == lookup_time]
        desired_adc = int(new_df.to_numpy()[0][3])                       # find desired adc based on time
        print("before")
        print(x) # to break the try
    except:
        try:
            time = datetime(2022,5,25,22,40,20)
            print(time)
            month = int(time.strftime("%m"))
            time_striffed = time.strftime("%H:%M:%S")
            time_stripped = datetime.strptime(time_striffed,"%H:%M:%S")
            month_df = adc_by_time.loc[adc_by_time['Month'] == month]
            lookup_time = timeround10(time_stripped)                         # rounds to nearest 10 min
            print(lookup_time)
            new_df = month_df.loc[month_df['Time'] == lookup_time]
            desired_adc = int(new_df.to_numpy()[0][3])   
            print("desired adc except:", desired_adc)
        except:
            desired_adc = 650
    return (desired_adc)


get_adc()


# In[ ]:




