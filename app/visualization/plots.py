# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 21:39:22 2020

@author: Juraj Majer
"""
import sys
sys.path.append('../..')

import pandas as pd
import plotly.express as px

from app.data import datasource as d
from dateutil.relativedelta import relativedelta

def get_plot_total_accident_trend(start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)['overallStartTime']
    df = prepare_data_for_trend_plot(data, start_datetime, end_datetime)
    
    fig = get_plot_accident_trend(df)
    return encode_plot(fig, output)

def get_plot_avg_accidents_by_weekdays(start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)['overallStartTime']
    data = data.map(lambda p: p.date())
    data = data.map(lambda p: p.weekday()).value_counts().sort_index() / pd.Series(data.unique()).map(lambda p: p.weekday()).value_counts().sort_index()
    df = pd.DataFrame(dict(weekday=data.index, avg_count=data.values))
    
    fig = px.bar(df, x='weekday', y='avg_count', labels={'avg_count':'Priemerný počet nehôd'}, hover_data={'weekday':False},)
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['weekday'],
            ticktext = get_weekday_xtickslabels(df['weekday']),
            title_text = 'Deň v týždni',
            titlefont=dict(size=20),
        ),
        height=500,
        yaxis = dict(
            title_text = 'Priemerný počet nehôd',
            gridcolor='rgb(140,140,140)',
            titlefont=dict(size=20),
        ),
        dragmode=False,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14,),
    )
    return encode_plot(fig, output)

def get_plot_total_accidents_by_county(start_datetime, end_datetime, output='json'):
    acc = d.get_traffic_accident_by_date(start_datetime, end_datetime)['countyId']
    acc = acc.value_counts()
    data = d.get_county()
    data['count'] = 0
    data['count'] += acc
    data['count'] = data['count'].fillna(0)
    data.sort_values(by='count', inplace=True)
    
    fig = px.bar(data, x='name', y='count', custom_data=[data.index], labels={'count':'Počet nehôd'}, hover_data={'name':False},)
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = data['name'],
            title_text = 'Kraj',
            titlefont=dict(size=20),
        ),
        height=600,
        yaxis = dict(
            title_text = 'Absolútny počet nehôd',
            gridcolor='rgb(140,140,140)',
            titlefont=dict(size=20),
        ),
        dragmode=False,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14,),
    )
    return encode_plot(fig, output)

def get_plot_total_accidents_by_district(start_datetime, end_datetime, output='json'):
    acc = d.get_traffic_accident_by_date(start_datetime, end_datetime)['districtId']
    acc = acc.value_counts()
    data = d.get_district()
    data['count'] = 0
    data['count'] += acc
    data['count'] = data['count'].fillna(0)
    data.sort_values(by='count', inplace=True)
    
    fig = px.bar(data, x='name', y='count', custom_data=[data.index], labels={'count':'Počet nehôd'}, hover_data={'name':False},)
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = data['name'],
            title_text = 'Okres',
            titlefont=dict(size=20),
        ),
        height=600,
        yaxis = dict(
            title_text = 'Absolútny počet nehôd',
            gridcolor='rgb(140,140,140)',
            titlefont=dict(size=20),
        ),
        dragmode=False,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14,),
    )
    return encode_plot(fig, output)

def get_plot_total_accidents_by_city(start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)['cityId']
    city_names = d.get_city()
    data = data.value_counts()
    data.index = data.index.map(lambda p: city_names.loc[p]['name'] if p in city_names.index else 'NA')
    zeroes = pd.Series(data=0, index=city_names.name)
    data = data + zeroes
    data = data.fillna(0)
    data = data.sort_values().tail(50)
    df = pd.DataFrame(dict(city=data.index, count=data.values))
    
    fig = px.bar(df, x='city', y='count', labels={'count':'Počet nehôd'}, hover_data={'city':False},)
    fig.update_layout(
        xaxis = dict(
            tickangle=90,
            tickmode = 'array',
            tickvals = df['city'],
            title_text = 'Obec',
            titlefont=dict(size=20),
        ),
        height=700,
        yaxis = dict(
            title_text = 'Absolútny počet nehôd',
            gridcolor='rgb(140,140,140)',
            titlefont=dict(size=20),
        ),
        dragmode=False,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14,),
    )
    return encode_plot(fig, output)

def get_plot_accident_by_time_in_day(start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)['overallStartTime']
    total_count = data.size
    data = data.map(lambda p: p.time().hour).value_counts().sort_index()
    data = data * 100 / total_count
    df = pd.DataFrame(dict(hour=data.index, pct=data.values))
    
    fig = px.bar(df, x='hour', y='pct', labels={'pct':'Percento nehôd'}, hover_data={'hour':False, 'pct':':.2f'},)
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['hour'],
            title_text = 'Hodina počas dňa',
            titlefont=dict(size=20),
        ),
        height=500,
        yaxis = dict(
            title_text = 'Percento nehôd',
            gridcolor='rgb(140,140,140)',
            titlefont=dict(size=20),
        ),
        dragmode=False,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14,),
    )
    return encode_plot(fig, output)

def get_plot_accident_trend_in_county(county_id, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.countyId == county_id]['overallStartTime']
    df = prepare_data_for_trend_plot(data, start_datetime, end_datetime)
    
    fig = get_plot_accident_trend(df)
    return encode_plot(fig, output)
    
def get_plot_accident_trend_in_district(district_id, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.districtId == district_id]['overallStartTime']
    df = prepare_data_for_trend_plot(data, start_datetime, end_datetime)
    
    fig = get_plot_accident_trend(df)
    return encode_plot(fig, output)

def get_plot_accident_trend_on_road(road_number, start_datetime, end_datetime, output='json'):
    data = d.get_traffic_accident_by_date(start_datetime, end_datetime)
    data = data.loc[data.roadNumber == road_number]['overallStartTime']
    df = prepare_data_for_trend_plot(data, start_datetime, end_datetime)
    
    fig = get_plot_accident_trend(df)
    return encode_plot(fig, output)

def prepare_data_for_trend_plot(data, start_datetime, end_datetime):
    data = data.map(lambda p: p.date())
    data = data.value_counts().sort_index()
    add_zeroes_datetime(data, start_datetime.date(), end_datetime.date())
    return pd.DataFrame(dict(date=data.index, count=data.values))

def get_plot_accident_trend(data):
    fig = px.bar(data, x='date', y='count', labels={'count':'Počet nehôd', 'date':'Dátum'},)
    fig.update_layout(
        xaxis = dict(
            #tickangle=-30,
            #tickmode = 'array',
            #tickvals = data['date'],
            tickformat = '%d. %m.',
            title_text = 'Deň',
            titlefont=dict(size=20),
        ),
        height=500,
        yaxis = dict(
            title_text = 'Počet nehôd',
            gridcolor='rgb(140,140,140)',
            titlefont=dict(size=20),
        ),
        dragmode=False,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14,),
    )
    return fig

def add_zeroes_datetime(df, s, e):
    c = s
    while c <= e:
        if c not in df:
            df[c] = 0
        c += relativedelta(days=1)

def get_weekday_xtickslabels(index, format='long'):
    fnc = get_long_week_day_name
    if format != 'long':
        fnc = get_short_week_day_name
    return [fnc(x) for x in index]

def get_long_week_day_name(weekDayCode):
    if weekDayCode == 0: return 'Pondelok'
    if weekDayCode == 1: return 'Utorok'
    if weekDayCode == 2: return 'Streda'
    if weekDayCode == 3: return 'Štvrtok'
    if weekDayCode == 4: return 'Piatok'
    if weekDayCode == 5: return 'Sobota'
    return 'Nedeľa'

def get_short_week_day_name(weekDayCode):
    return get_long_week_day_name(weekDayCode)[0:3]
 
def encode_plot(fig, output=None):
    if output == 'html':
        return fig.to_html(include_plotlyjs=False, full_html=False)
    if output == 'json':
        return fig.to_json()
    fig.show(renderer="browser")
    
#get_plot_total_accidents_by_county(output=None)
#get_plot_total_accidents_by_weekdays()
#get_plot_total_accidents_by_days()
#print(get_start_date(None))
#print(get_end_date(None))
#from datetime import datetime
#s = datetime.strptime('2021-01-06', '%Y-%m-%d')
#s = s.replace(hour=0, minute=0, second=0, microsecond=0)
#e = datetime.strptime('2021-02-05', '%Y-%m-%d')
#e = e.replace(hour=23, minute=59, second=59, microsecond=999999)
#get_plot_total_accidents_by_district(s, e, None)