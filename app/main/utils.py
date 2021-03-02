# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 22:03:18 2020

@author: Juraj Majer
"""

from timeit import default_timer as t
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.data import datasource as d

perf_time_start = 0

def perf_start():
    global perf_time_start
    perf_time_start = t()
    
def perf_lap(msg = None):
    global perf_time_start
    if msg is not None:
        msg += " "
    else:
        msg = ""
    end = t()
    msg += str((end - perf_time_start))
    perf_time_start = end
    print(msg)
    
# Calculates distance between 2 GPS coordinates
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def get_min_date():
    retval = d.get_traffic_accident_by_date()['overallStartTime'].min()
    retval = retval.replace(hour=0, minute=0, second=0, microsecond=0)
    return retval

def get_max_date():
    e = datetime.now() - relativedelta(days=1)
    e = e.replace(hour=23, minute=59, second=59, microsecond=999999)
    return e