# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 22:09:05 2020

@author: Juraj Majer
"""
import sys
sys.path.append('../..')

from app.data import models as m
import pandas as pd

def get_traffic_accident_by_date(start_date=None, end_date=None):
    retval = []
    items = m.TrafficAccident.query.all()
    if start_date is not None or end_date is not None:
        for item in items:
            if start_date is not None and start_date > item.overallStartTime:
                continue
            if end_date is not None and end_date < item.overallStartTime:
                continue
            retval.append(item)
    else:
        retval = items
    return pd.DataFrame(data=[[x.id, x.overallStartTime, x.sourceName, x.longitude, x.latitude, x.countyId, x.districtId] for x in retval],
                        columns=['id', 'overallStartTime', 'sourceName', 'longitude', 'latitude', 'countyId', 'districtId'])
    
def get_district():
    items = m.District.query.all()
    return pd.DataFrame(index=[x.id for x in items],
                        data=[[x.name] for x in items],
                        columns=['name'])
    
def get_county():
    items = m.County.query.all()
    return pd.DataFrame(index=[x.id for x in items],
                        data=[[x.name] for x in items],
                        columns=['name'])
    