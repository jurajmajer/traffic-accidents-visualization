# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 22:09:05 2020

@author: Juraj Majer
"""
import sys
sys.path.append('../..')

from app.data import models as m
import pandas as pd
from app import cache
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import aliased

def get_traffic_accident_by_date(start_date=None, end_date=None):
    retval = get_traffic_accident()
    if start_date is not None:
        retval= retval[retval['overallStartTime'] > start_date]
    if end_date is not None:
        retval= retval[retval['overallStartTime'] < end_date]
    return retval

@cache.cached(timeout=43200, key_prefix='get_district')
def get_district():
    items = m.District.query.all()
    return pd.DataFrame(index=[x.id for x in items],
                        data=[[x.name] for x in items],
                        columns=['name'])    
    
@cache.cached(timeout=43200, key_prefix='get_county')
def get_county():
    items = m.County.query.all()
    return pd.DataFrame(index=[x.id for x in items],
                        data=[[x.name] for x in items],
                        columns=['name'])
    
@cache.cached(timeout=43200, key_prefix='get_city')
def get_city():
    items = m.City.query.all()
    return pd.DataFrame(index=[x.id for x in items],
                        data=[[x.name] for x in items],
                        columns=['name'])
    
def get_nearby_accidents_for_road(max_distance, county_id=None, district_id=None, city_id=None, road_number=None, start_date=None, end_date=None):
    trafficAccident1 = aliased(m.TrafficAccident)
    trafficAccident2 = aliased(m.TrafficAccident)
    
    query = m.NearbyAccident.query \
    .join(trafficAccident1, m.NearbyAccident.accident1_id==trafficAccident1.id) \
    .join(trafficAccident2, m.NearbyAccident.accident2_id==trafficAccident2.id) \
    .filter(m.NearbyAccident.distance<max_distance)
    
    if county_id is not None:
        query = query.filter(trafficAccident1.countyId == county_id)
        query = query.filter(trafficAccident2.countyId == county_id)
        
    if district_id is not None:
        query = query.filter(trafficAccident1.districtId == district_id)
        query = query.filter(trafficAccident2.districtId == district_id)
        
    if city_id is not None:
        query = query.filter(trafficAccident1.cityId == city_id)
        query = query.filter(trafficAccident2.cityId == city_id)
    
    if road_number is not None:
        query = query.filter(trafficAccident1.roadNumber == road_number)
        query = query.filter(trafficAccident2.roadNumber == road_number)
    
    if start_date is not None:
        query = query.filter(trafficAccident1.overallStartTime > start_date)
        query = query.filter(trafficAccident2.overallStartTime > start_date)
        
    if end_date is not None:
        query = query.filter(trafficAccident1.overallStartTime < end_date)
        query = query.filter(trafficAccident2.overallStartTime < end_date)
    
    return query.all()

def get_traffic_accident():
    cache_timestamp_key = 'get_traffic_accident_timestamp'
    cache_key = 'get_traffic_accident'
    
    is_valid = is_data_valid(cache_timestamp_key, 86400)
    if is_valid:
        return cache.get(cache_key)
        
    items = m.TrafficAccident.query.all()
    retval = pd.DataFrame(data=[[x.id, x.overallStartTime, x.sourceName, x.longitude, x.latitude, x.countyId, x.districtId, x.cityId, x.roadNumber] for x in items],
                        columns=['id', 'overallStartTime', 'sourceName', 'longitude', 'latitude', 'countyId', 'districtId', 'cityId', 'roadNumber'])
    cache.set(cache_key, retval)
    cache.set(cache_timestamp_key, datetime.now())
    return retval

def is_data_valid(cache_timestamp_key, timeout, must_be_same_day=True):
    timestamp = cache.get(cache_timestamp_key)
    if timestamp is None:
        return False
    now = datetime.now()
    if must_be_same_day and now.date() > timestamp.date():
        return False
    limit = now - relativedelta(seconds=timeout)
    if timestamp < limit:
        return False
    return True