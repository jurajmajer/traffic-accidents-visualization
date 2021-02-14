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
import pandas as pd
import json
import os

def get_district_detail_map(district_id, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data[data['districtId']==district_id]
    data['marker_size'] = 10
    center_lat = (data['latitude'].min() + data['latitude'].max()) / 2
    center_lon = (data['longitude'].min() + data['longitude'].max()) / 2
    
    return get_accident_scatter_map(data, output, 10, {'lat':center_lat, 'lon':center_lon})

def get_district_choropleth(start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)['districtId']
    district_names = d.get_district()
    data = data.value_counts()
    data.index = data.index.map(lambda p: district_names.loc[p]['name'])
    zeroes = pd.Series(data=0, index=district_names.name)
    data = data + zeroes
    data = data.fillna(0)
    data = data.sort_values()
    df = pd.DataFrame(dict(district=data.index, count=data.values))
    geojson_file = os.path.join(os.path.dirname(__file__), 'districts_epsg_4326.geojson.txt')
    with open(geojson_file, encoding='utf-8') as file:
        geo_districts = json.loads(file.read())
    fig = px.choropleth(data_frame=df, geojson=geo_districts, featureidkey='properties.NM3', locations='district', color='count',
                           color_continuous_scale='tealrose',
                           range_color=(0, df['count'].mean()*2),
                           projection='sinusoidal', 
                           labels={'count':'Počet nehôd', 'district':'Okres'},
                           title='Celkový počet nehôd podľa okresu')
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    return plots.encode_plot(fig, output)
    
def get_accident_scatter_map(data, output, zoom, center):
    fig = px.scatter_mapbox(data, lat='latitude', lon='longitude',
                  mapbox_style="open-street-map", size='marker_size', size_max=10, opacity=0.8, hover_name='overallStartTime',
                  hover_data=['overallStartTime'], zoom=zoom)
    return plots.encode_plot(fig, output)
    