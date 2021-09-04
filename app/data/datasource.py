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

@cache.cached(timeout=43200, key_prefix='get_road')
def get_road():
    items = m.Road.query.all()
    return pd.DataFrame(index=[x.id for x in items],
                        data=[[x.number, x.classification, x.direction, x.shape_length] for x in items],
                        columns=['number', 'classification', 'direction', 'shape_length'])
    
def get_road_shape(road_number):
    retval = m.Road.query.filter(m.Road.number == road_number).filter(m.Road.direction == 1).all()
    if len(retval) == 1:
        return retval[0].shape
    return None
    
def get_nearby_accidents(max_distance, county_id=None, district_id=None, city_id=None, road_number=None, start_date=None, end_date=None):
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
    refresh_timestamp_key = 'get_traffic_accident_refresh_timestamp'
    cache_key = 'get_traffic_accident'
    
    is_valid = is_data_valid(refresh_timestamp_key)
    if is_valid:
        return cache.get(cache_key)
        
    items = m.TrafficAccident.query.all()
    retval = pd.DataFrame(data=[[x.id, x.overallStartTime, x.sourceName, x.longitude, x.latitude, x.countyId, x.districtId, x.cityId, x.roadNumber, x.roadPosition] for x in items],
                        columns=['id', 'overallStartTime', 'sourceName', 'longitude', 'latitude', 'countyId', 'districtId', 'cityId', 'roadNumber', 'roadPosition'])
    cache.set(cache_key, retval, timeout=0)
    refresh_timestamp = datetime.now() + relativedelta(days=1)
    refresh_timestamp = refresh_timestamp.replace(hour=1, minute=0, second=0, microsecond=0)
    cache.set(refresh_timestamp_key, refresh_timestamp, timeout=0)
    return retval

def get_nearby_accident():
    refresh_timestamp_key = 'get_nearby_accident_refresh_timestamp'
    cache_key = 'get_nearby_accident'
    
    is_valid = is_data_valid(refresh_timestamp_key)
    if is_valid:
        return cache.get(cache_key)
        
    items = m.NearbyAccident.query.filter(m.NearbyAccident.distance<0.5).all()
    retval = pd.DataFrame(data=[[x.id, x.accident1_id, x.accident2_id, x.distance] for x in items],
                        columns=['id', 'accident1_id', 'accident2_id', 'distance'])
    cache.set(cache_key, retval, timeout=0)
    refresh_timestamp = datetime.now() + relativedelta(days=1)
    refresh_timestamp = refresh_timestamp.replace(hour=1, minute=0, second=0, microsecond=0)
    cache.set(refresh_timestamp_key, refresh_timestamp, timeout=0)
    return retval

def is_data_valid(refresh_timestamp_key):
    refresh_timestamp = cache.get(refresh_timestamp_key)
    if refresh_timestamp is None:
        return False
    now = datetime.now()
    if refresh_timestamp < now:
        return False
    return True
    