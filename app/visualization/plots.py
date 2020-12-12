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
from datetime import datetime
from dateutil.relativedelta import relativedelta
#from app.main import utils as u

def get_now_datetime():
    retval = datetime.now()
    return retval.replace(hour=0, minute=0, second=0, microsecond=0)

def get_start_datetime(start_datetime):
    if start_datetime is not None:
        return start_datetime
    return get_now_datetime() - relativedelta(days=61)

def get_end_datetime(end_datetime):
    if end_datetime is not None:
        return end_datetime
    return get_now_datetime()

def get_plot_total_accidents_by_days(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['overallStartTime']
    data = data.map(lambda p: p.date()).value_counts().sort_index()
    df = pd.DataFrame(dict(date=data.index, count=data.values))
    
    fig = px.bar(df, x='date', y='count', title="Histogram nehôd - počet nehôd za deň")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['date'],
            ticktext = get_date_xtickslabels(df['date']),
            title_text = 'Deň'
        ),
        yaxis = dict(
            title_text = 'Počet nehôd'
        )
    )
    
    return encode_plot(fig)
    #fig.show(renderer="browser")

def get_plot_avg_accidents_by_weekdays(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['overallStartTime']
    data = data.map(lambda p: p.date())
    data = data.map(lambda p: p.weekday()).value_counts().sort_index() / pd.Series(data.unique()).map(lambda p: p.weekday()).value_counts().sort_index()
    df = pd.DataFrame(dict(weekday=data.index, avg_count=data.values))
    
    fig = px.bar(df, x='weekday', y='avg_count', title="Priemerný počet nehôd podľa dňa v týždni")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['weekday'],
            ticktext = get_weekday_xtickslabels(df['weekday']),
            title_text = 'Deň v týždni'
        ),
        yaxis = dict(
            title_text = 'Priemerný počet nehôd'
        )
    )
    return encode_plot(fig)
    #fig.show(renderer="browser")

def get_plot_total_accidents_by_county(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['countyId']
    county_names = d.get_county()
    data = data.map(lambda p: county_names.loc[p]['name'])
    data = data.value_counts().sort_values()
    df = pd.DataFrame(dict(county=data.index, count=data.values))
    
    fig = px.bar(df, x='county', y='count', title="Absolútny počet nehôd podľa kraju")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['county'],
            title_text = 'Kraj'
        ),
        yaxis = dict(
            title_text = 'Absolútny počet nehôd'
        )
    )
    return encode_plot(fig)
    #fig.show(renderer="browser")

def get_plot_total_accidents_by_district(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['districtId']
    district_names = d.get_district()
    data = data.map(lambda p: district_names.loc[p]['name']).value_counts()
    zeroes = pd.Series(data=0, index=district_names.name)
    data = data + zeroes
    data = data.fillna(0)
    data = data.sort_values()
    df = pd.DataFrame(dict(district=data.index, count=data.values))
    
    fig = px.bar(df, x='district', y='count', title="Absolútny počet nehôd podľa okresu")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['district'],
            title_text = 'Kraj'
        ),
        yaxis = dict(
            title_text = 'Absolútny počet nehôd'
        )
    )
    return encode_plot(fig)
    #fig.show(renderer="browser")

def get_plot_accident_trend_in_county(county_id, start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))
    data = data.loc[data.countyId == county_id]['overallStartTime']
    data = data.map(lambda p: p.date())
    data = data.value_counts().sort_index()
    df = pd.DataFrame(dict(date=data.index, count=data.values))
    
    county_names = d.get_county()
    fig = px.line(df, x='date', y='count', title="Vývoj nehôd v čase pre " + county_names.loc[county_id]['name'])
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['date'],
            ticktext = get_date_xtickslabels(df['date']),
            title_text = 'Deň'
        ),
        yaxis = dict(
            title_text = 'Počet nehôd'
        )
    )
    return encode_plot(fig)
    #fig.show(renderer="browser")
    
def get_plot_accident_trend_in_district(district_id, start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))
    data = data.loc[data.districtId == district_id]['overallStartTime']
    data = data.map(lambda p: p.date())
    data = data.value_counts().sort_index()
    df = pd.DataFrame(dict(date=data.index, count=data.values))
    
    district_names = d.get_district()
    fig = px.line(df, x='date', y='count', title="Vývoj nehôd v čase pre okres " + district_names.loc[district_id]['name'])
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['date'],
            ticktext = get_date_xtickslabels(df['date']),
            title_text = 'Deň'
        ),
        yaxis = dict(
            title_text = 'Počet nehôd'
        )
    )
    return encode_plot(fig)
    #fig.show(renderer="browser")

def get_plot_accident_by_time_in_day(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['overallStartTime']
    total_count = data.size
    data = data.map(lambda p: p.time().hour).value_counts().sort_index()
    data = data * 100 / total_count
    df = pd.DataFrame(dict(hour=data.index, pct=data.values))
    
    fig = px.bar(df, x='hour', y='pct', title="Percento nehôd podľa hodiny v dni")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = df['hour'],
            title_text = 'Hodina počas dňa'
        ),
        yaxis = dict(
            title_text = 'Percento nehôd'
        )
    )
    return encode_plot(fig)
    #fig.show(renderer="browser")
    
def get_date_xtickslabels(index, date_format='%d.%m.'):
    return [x.strftime(date_format) + ' (' + get_short_week_day_name(x.weekday()) + ')' for x in index]

def get_weekday_xtickslabels(index, format='long'):
    fnc = get_long_week_day_name
    if format != 'long':
        fnc = get_short_week_day_name
    return [fnc(x) for x in index]

def get_min_max_colors(values, minc='lawngreen', maxc='gold', otherc='silver'):
    retval = []
    minimum = min(values)
    maximum = max(values)
    
    for val in values:
        c = otherc
        if val == maximum:
            c = maxc
        elif val == minimum:
            c = minc
        retval.append(c)
    
    return retval

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
 
def encode_plot(fig):
    return fig.to_html(include_plotlyjs=False, full_html=False)
    
#get_plot_accident_by_time_in_day()
#get_plot_total_accidents_by_weekdays()
#get_plot_total_accidents_by_days()
#print(get_start_date(None))
#print(get_end_date(None))