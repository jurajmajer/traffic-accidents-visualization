# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 23:29:00 2021

@author: Juraj Majer
"""
import sys
sys.path.append('../..')

import plotly.express as px
from app.data import datasource as d
from app.visualization import plots

def get_map(start_datetime, end_datetime, output='json'):
    
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data['marker_size'] = 10
    center_lat = (data['latitude'].min() + data['latitude'].max()) / 2
    center_lon = (data['longitude'].min() + data['longitude'].max()) / 2
    
    return get_accident_scatter_map(data, output, 8, {'lat':center_lat, 'lon':center_lon})

def get_district_detail_map(district_id, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data[data['districtId']==district_id]
    data['marker_size'] = 10
    center_lat = (data['latitude'].min() + data['latitude'].max()) / 2
    center_lon = (data['longitude'].min() + data['longitude'].max()) / 2
    
    return get_accident_scatter_map(data, output, 10, {'lat':center_lat, 'lon':center_lon})

def get_accident_scatter_map(data, output, zoom, center):
    fig = px.scatter_mapbox(data, lat='latitude', lon='longitude',
                  mapbox_style="open-street-map", size='marker_size', size_max=10, opacity=0.8, hover_name='overallStartTime',
                  hover_data=['overallStartTime'], zoom=zoom)
    return plots.encode_plot(fig, output)
    