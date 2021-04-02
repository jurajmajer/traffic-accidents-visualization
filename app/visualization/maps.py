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
from timeit import default_timer as tim

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
                           labels={'count':'Počet nehôd'},
                           hover_data={'district':False},
                           hover_name=df['district'],
                           title='Celkový počet nehôd podľa okresu')
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor= 'rgba(0,0,0,0)'),
    )
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
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor= 'rgba(0,0,0,0)'),
    )
    return plots.encode_plot(fig, output)

def calculate_marker_size(x, minM, maxM):
    if minM == maxM:
        return 10
    return 5 + (x['marker_size']-minM) * 45 / (maxM-minM)

def get_map_with_most_frequent_accidents_for_road(road_number, max_number_accidents_returned, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.roadNumber == road_number]
    return get_map_with_most_frequent_accidents(max_number_accidents_returned, data, 8, output)

def get_map_with_most_frequent_accidents_for_county(county_id, max_number_accidents_returned, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.countyId == county_id]
    return get_map_with_most_frequent_accidents(max_number_accidents_returned, data, 8, output)

def get_map_with_most_frequent_accidents_for_district(district_id, max_number_accidents_returned, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.districtId == district_id]
    return get_map_with_most_frequent_accidents(max_number_accidents_returned, data, 9, output)

def get_map_with_most_frequent_accidents(max_number_accidents_returned, data, zoom, output='json'):
    data=filter_nearby_accidents(data)
    temp = []
    retval = []
    for i, row in data.iterrows():
        is_already_counted = False
        for t in temp:
            if u.haversine(t[2], t[1], row['latitude'], row['longitude']) < 0.5:
                is_already_counted = True
                break
        if not is_already_counted:
            temp.append([row['id'], row['longitude'], row['latitude']])
            retval.append(row['id'])
        if len(temp) >= max_number_accidents_returned:
            break
    data = data.loc[data['id'].isin(retval)]
    data['order'] = range(1,len(data.index)+1)
    minM = data['marker_size'].min()
    maxM = data['marker_size'].max()
    data['projected_marker_size'] = data.apply(lambda x: calculate_marker_size(x, minM, maxM), axis=1)
    
    fig = px.scatter_mapbox(data, lat='latitude', lon='longitude',
                  mapbox_style='open-street-map', size='projected_marker_size', size_max=data['projected_marker_size'].max(), 
                  opacity=0.8, color='marker_size', color_continuous_scale='Bluered',
                  labels={'marker_size':'Počet nehôd v danom období', 'order':'Poradie nehodového úseku'}, 
                  hover_data={'latitude':False, 'longitude':False, 'order':True, 'projected_marker_size':False}, zoom=zoom,
                  center = {'lat':data.iloc[0]['latitude'], 'lon':data.iloc[0]['longitude']})
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
    )
    return plots.encode_plot(fig, output)

def sum_values(a, b, idx):
    retval = 0
    if idx in a:
        retval += a[idx]
    if idx in b:
        retval += b[idx]
    return retval

def filter_nearby_accidents(data):
    retval = d.get_nearby_accident()
    retval = retval.loc[(retval['accident1_id'].isin(data['id'])) & (retval['accident2_id'].isin(data['id']))]
    a = retval['accident1_id'].value_counts()
    b = retval['accident2_id'].value_counts()
    data['marker_size'] = data.apply(lambda x: sum_values(a, b, x['id']), axis=1)
    return data.sort_values(by='marker_size', ascending=False)
    
def get_accident_scatter_map(data, output, zoom, center):
    fig = px.scatter_mapbox(data, lat='latitude', lon='longitude',
                  mapbox_style="open-street-map", size='marker_size', size_max=10, opacity=0.8, hover_name='overallStartTime',
                  hover_data=['overallStartTime'], zoom=zoom)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
    )
    return plots.encode_plot(fig, output)
    
#s = datetime.strptime('2021-01-06', '%Y-%m-%d')
#s = s.replace(hour=0, minute=0, second=0, microsecond=0)
#e = datetime.strptime('2021-02-05', '%Y-%m-%d')
#e = e.replace(hour=23, minute=59, second=59, microsecond=999999)
#get_map_with_most_frequent_accidents_for_road('D3', 20, s, e)
#get_map_with_most_frequent_accidents_for_road2('D3', 20, None, None)
#s = tim()
#df=d.get_nearby_accident()
#print(len(df.index))
#print(str(tim() - s) + 's')
#s = tim()
#get_map_with_most_frequent_accidents_for_district(102, 20, None, None)
#print(str(tim() - s) + 's')
    
#s = tim()
#data = d.get_traffic_accident_by_date(None, None)
#print(str(tim() - s) + 's')
#s = tim()
#data = data.loc[data.districtId == 102]
#print(str(tim() - s) + 's')
#s = tim()
#data=filter_nearby_accidents(data)
#print(str(tim() - s) + 's')
#s = tim()
#print(data)
    
#get_map_with_most_frequent_accidents_for_district(102, 20, None, None)