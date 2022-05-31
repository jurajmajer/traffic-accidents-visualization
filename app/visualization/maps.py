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
import plotly.graph_objects as go

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
                           hover_name=df['district'])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor= 'rgba(0,0,0,0)'),
            coloraxis_showscale=False,
    )
    return plots.encode_plot(fig, output)

def get_county_choropleth(start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)['countyId']
    county_names = d.get_county()
    data = data.value_counts()
    data.index = data.index.map(lambda p: county_names.loc[p]['name'])
    zeroes = pd.Series(data=0, index=county_names.name)
    data = data + zeroes
    data = data.fillna(0)
    data = data.sort_values()
    df = pd.DataFrame(dict(county=data.index, count=data.values))
    
    geojson_file = os.path.join(os.path.dirname(__file__), 'regions_epsg_4326.geojson.txt')
    with open(geojson_file, encoding='utf-8') as file:
        geo_counties = json.loads(file.read())
    fig = px.choropleth(data_frame=df, geojson=geo_counties, featureidkey='properties.NM4', locations='county', color='count',
                           color_continuous_scale='tealrose',
                           range_color=(0, df['count'].mean()*2),
                           projection='sinusoidal', 
                           labels={'count':'Počet nehôd'},
                           hover_data={'county':False},
                           hover_name=df['county'])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor= 'rgba(0,0,0,0)'),
            coloraxis_showscale=False,
    )
    return plots.encode_plot(fig, output)

def calculate_marker_size(x, minM, maxM):
    if minM == maxM:
        return 10
    return 5 + (x['marker_size']-minM) * 45 / (maxM-minM)

def get_map_with_most_frequent_accidents_for_country(max_number_accidents_returned, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    fig = get_map_with_most_frequent_accidents(max_number_accidents_returned, data, 6, center = {'lat':48.663863, 'lon':19.502998})
    return plots.encode_plot(fig, output)

def get_map_with_most_frequent_accidents_for_road(road_number, max_number_accidents_returned, start_datetime, end_datetime, start_km=0, end_km=999999999, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.roadNumber == road_number]
    data = data.loc[(data.roadPosition >= start_km) & (data.roadPosition <= end_km)]
    fig = get_map_with_most_frequent_accidents(max_number_accidents_returned, data, 8)
    if data.size > 0:
        shape = d.get_road_shape(road_number)
        if shape is not None:
            shape_list = parse_shape_string(shape)
            shape_list = filter_shape(shape_list, start_km, end_km)
            for s in shape_list:
                fig.add_trace(go.Scattermapbox(
                    mode = 'lines',
                    line=dict(width=4, color="#006699"),
                    showlegend=False,
                    lon = s[1],
                    lat = s[0],
                    hoverinfo='skip'))
    return plots.encode_plot(fig, output)

def get_map_with_most_frequent_accidents_for_county(county_id, max_number_accidents_returned, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.countyId == county_id]
    fig = get_map_with_most_frequent_accidents(max_number_accidents_returned, data, 8.5)
    return plots.encode_plot(fig, output)

def get_map_with_most_frequent_accidents_for_district(district_id, max_number_accidents_returned, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.districtId == district_id]
    fig = get_map_with_most_frequent_accidents(max_number_accidents_returned, data, 9.5)
    return plots.encode_plot(fig, output)

def get_map_accident_detail(latitude, longitude, hover_text, output='json'):
    data = pd.DataFrame(columns=['latitude', 'longitude', 'marker_size'])
    data.loc[0] = [latitude, longitude, 50]
    return get_accident_scatter_map(data, output, 14, {'lat':latitude, 'lon':longitude})

def get_map_with_most_frequent_accidents(max_number_accidents_returned, data, zoom, center=None):
    data=filter_nearby_accidents(data)
    if data is None:
        # return plots.get_empty_plot()
        return plots.get_simple_plot_with_text("Nie je k dispozícii")
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
    if center is None:
        center = {'lat':data.iloc[0]['latitude'], 'lon':data.iloc[0]['longitude']}
    
    fig = px.scatter_mapbox(data, lat='latitude', lon='longitude',
                  mapbox_style='open-street-map', size='projected_marker_size', size_max=data['projected_marker_size'].max(), 
                  opacity=0.8, color='marker_size', color_continuous_scale=["blue", "red"],
                  labels={'marker_size':'Počet nehôd v danom období', 'order':'Poradie nehodového úseku'}, 
                  hover_data={'latitude':False, 'longitude':False, 'order':True, 'projected_marker_size':False}, zoom=zoom,
                  center = center)
        
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
    )
    
    return fig

def sum_values(a, b, idx):
    retval = 0
    if idx in a:
        retval += a[idx]
    if idx in b:
        retval += b[idx]
    retval += 1
    return retval

def filter_nearby_accidents(data):
    return None
    if len(data.index) == 0:
        return None
    retval = d.get_nearby_accident()
    retval = retval.loc[(retval['accident1_id'].isin(data['id'])) & (retval['accident2_id'].isin(data['id']))]
    a = []
    b = []
    if len(retval) > 0:
        a = retval['accident1_id'].value_counts()
        b = retval['accident2_id'].value_counts()
    data['marker_size'] = data.apply(lambda x: sum_values(a, b, x['id']), axis=1)
    return data.sort_values(by='marker_size', ascending=False)
    
def get_accident_scatter_map(data, output, zoom, center, size_max = None):
    if size_max is None:
        size_max = 50
    fig = px.scatter_mapbox(data, lat='latitude', lon='longitude',
                  mapbox_style="open-street-map", size='marker_size', size_max=size_max, opacity=0.8,
                  hover_data={'latitude':False, 'longitude':False, 'marker_size':False}, zoom=zoom, center = center)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
    )
    return plots.encode_plot(fig, output)

def parse_shape_string(shape_string):
    retval = []
    if shape_string.startswith('['):
        shape_string = shape_string[1:-1]
        shape_string = shape_string.replace('\'', '')
        for x in shape_string.split(','):
            retval.append(parse_line_string(x))
    else:
        retval.append(parse_line_string(shape_string))
    return retval

def parse_line_string(line_string):
    line_string = line_string.strip()
    parts = line_string.split()
    lat = []
    lon = []
    for i in range(0, int(len(parts)/2)):
        lat.append(float(parts[2*i]))
        lon.append(float(parts[2*i+1]))
    return [lat, lon]

def filter_shape(shape, start_km, end_km):
    if start_km == 0 and end_km >= 999999999:
        return shape
    retval = []
    distance = 0
    for line_string in shape:
        ls_lat = []
        ls_lon = []
        for i in range(len(line_string[0])):
            if i > 0:
                distance += u.haversine(line_string[0][i-1], line_string[1][i-1], line_string[0][i], line_string[1][i])
            if start_km <= distance and distance <= end_km:
                ls_lat.append(line_string[0][i])
                ls_lon.append(line_string[1][i])
            if distance > end_km:
                break
        if len(ls_lat) > 1:
            retval.append([ls_lat, ls_lon])
        if distance > end_km:
            break
    return retval
    
    
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