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
from app.main import utils as u

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

def get_county_detail_map(county_id, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data[data['countyId']==county_id]
    data['marker_size'] = 10
    center_lat = (data['latitude'].min() + data['latitude'].max()) / 2
    center_lon = (data['longitude'].min() + data['longitude'].max()) / 2
    
    return get_accident_scatter_map(data, output, 9, {'lat':center_lat, 'lon':center_lon})

def get_county_choropleth(start_datetime, end_datetime, output='json'):
    acc = d.get_traffic_accident_by_date(start_datetime, end_datetime)['countyId']
    acc = acc.value_counts()
    data = d.get_county()
    data['count'] = 0
    data['count'] += acc
    data['count'] = data['count'].fillna(0)
    
    geojson_file = os.path.join(os.path.dirname(__file__), 'regions_epsg_4326.geojson.txt')
    with open(geojson_file, encoding='utf-8') as file:
        geo_counties = json.loads(file.read())
    fig = px.choropleth(data_frame=data, geojson=geo_counties, featureidkey='properties.IDN4', locations=data.index, color='count',
                           color_continuous_scale='tealrose',
                           range_color=(0, data['count'].mean()*2),
                           projection='sinusoidal', 
                           labels={'count':'Počet nehôd', 'index':'Kraj'},
                           hover_name=data['name'],
                           title='Celkový počet nehôd podľa kraju')
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    return plots.encode_plot(fig, output)

def get_map_with_most_frequent_accidents_for_road(road_number, max_number_accidents_returned, start_datetime, end_datetime, output='json'):
    RADIUS = 0.5
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.roadNumber == road_number]
    temp = []
    for i, row in data.iterrows():
        temp.append([row['id'], row['longitude'], row['latitude']])
    acc_nearby = calculate_accidents_nearby_for_road(temp, RADIUS)
    acc_nearby = {k: v for k, v in sorted(acc_nearby.items(), key=lambda item: -1*len(item[1]))}
    used = set()
    retval = []
    i = 0
    for acc in acc_nearby.keys():
        if i >= max_number_accidents_returned:
            break
        if acc in used:
            continue
        print(str(acc) + ' : ' + str(len(acc_nearby[acc])))
        used = set.union(used, acc_nearby[acc])
        retval.append(acc)
        i += 1
    data = data.loc[data['id'].isin(retval)]
    data['marker_size'] = 10
    center_lat = (data['latitude'].min() + data['latitude'].max()) / 2
    center_lon = (data['longitude'].min() + data['longitude'].max()) / 2
    return get_accident_scatter_map(data, output, 8, {'lat':center_lat, 'lon':center_lon})

def calculate_accidents_nearby_for_road(accidents, radius):
    retval = {}
    for i in range(len(accidents)):
        this_accident = accidents[i]
        if this_accident[0] not in retval:
            retval[this_accident[0]] = set()
        for j in range(len(accidents)):
            if i >= j:
                continue
            a = accidents[j]
            distance = u.haversine(this_accident[2], this_accident[1], a[2], a[1])
            if distance < radius:
                if a[0] not in retval:
                    retval[a[0]] = set()
                retval[this_accident[0]].add(a[0])
                retval[a[0]].add(this_accident[0])
    return retval
    
def get_accident_scatter_map(data, output, zoom, center):
    fig = px.scatter_mapbox(data, lat='latitude', lon='longitude',
                  mapbox_style="open-street-map", size='marker_size', size_max=10, opacity=0.8, hover_name='overallStartTime',
                  hover_data=['overallStartTime'], zoom=zoom)
    return plots.encode_plot(fig, output)
    
#s = datetime.strptime('2021-01-06', '%Y-%m-%d')
#s = s.replace(hour=0, minute=0, second=0, microsecond=0)
#e = datetime.strptime('2021-02-05', '%Y-%m-%d')
#e = e.replace(hour=23, minute=59, second=59, microsecond=999999)
#get_map_with_most_frequent_accidents_for_road('D1', 20, s, e)