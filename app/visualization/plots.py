# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 21:39:22 2020

@author: Juraj Majer
"""
import sys
sys.path.append('../..')

# TODO: explore plotly 

import pandas as pd
import matplotlib
#matplotlib.use('qt5agg')
matplotlib.use('agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from app.data import datasource as d
from datetime import datetime
from dateutil.relativedelta import relativedelta
import seaborn as sns
from timeit import default_timer as t

# https://matplotlib.org/3.1.0/gallery/color/named_colors.html
# timing: print(t())

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
    days = data.map(lambda p: p.date()).value_counts().sort_index()
    
    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(25,15))
    plt.title("Histogram nehôd - počet nehôd za deň", fontsize=30, pad=20)
    plt.subplots_adjust(left=0.07, right=0.99)
    g = sns.barplot(x=days.index, y=days.values, palette=get_min_max_colors(days.values))
    #g.set_xlabel("Deň",fontsize=30, labelpad=15)
    g.set_ylabel("Počet nehôd",fontsize=30, labelpad=20)
    g.set_xticklabels(get_date_xtickslabels(days.index), rotation=90, fontsize=20)
    g.tick_params(axis='y', labelsize=25)
    return encode_plot(fig)

def get_plot_avg_accidents_by_weekdays(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['overallStartTime']
    data = data.map(lambda p: p.date())
    avg_accident_per_weekdays = data.map(lambda p: p.weekday()).value_counts().sort_index() / pd.Series(data.unique()).map(lambda p: p.weekday()).value_counts().sort_index()
    
    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(25,15))
    plt.title("Priemerný počet nehôd podľa dňa v týždni", fontsize=30, pad=20)
    plt.subplots_adjust(left=0.07, right=0.99)
    g = sns.barplot(x=avg_accident_per_weekdays.index, y=avg_accident_per_weekdays.values, palette=get_min_max_colors(avg_accident_per_weekdays.values))
    #g.set_xlabel("Deň v týždni",fontsize=30, labelpad=15)
    g.set_ylabel("Priemerný počet nehôd",fontsize=30, labelpad=20)
    g.set_xticklabels(get_weekday_xtickslabels(avg_accident_per_weekdays.index), rotation=45, fontsize=30)
    g.tick_params(axis='y', labelsize=25)
    return encode_plot(fig)

def get_plot_accidents_by_county(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['countyId']
    data = data.value_counts().sort_values()
    
    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(25,15))
    plt.title("Absolútny počet nehôd podľa kraju", fontsize=30, pad=20)
    plt.subplots_adjust(top=0.93, bottom=0.18, left=0.07, right=0.99)
    g = sns.barplot(x=get_county_xticklabels(data.index), y=data.values, palette=get_min_max_colors(data.values))
    g.set_ylabel("Absolútny počet nehôd",fontsize=30, labelpad=20)
    g.set_xticklabels(get_county_xticklabels(data.index), rotation=45, fontsize=20)
    g.tick_params(axis='y', labelsize=25)
    return encode_plot(fig)

def get_plot_accidents_by_district(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['districtId']
    data = data.value_counts()
    zeroes = pd.Series(index=d.get_district().index)
    zeroes.values[:] = 0
    zeroes += data
    data = zeroes.fillna(0).sort_values()
    
    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(25,15))
    fig.tight_layout()
    plt.title("Absolútny počet nehôd podľa okresu", fontsize=30, pad=20)
    plt.subplots_adjust(top=0.93, bottom=0.2, left=0.07, right=0.99)
    g = sns.barplot(x=get_district_xticklabels(data.index), y=data.values, palette=get_min_max_colors(data.values))
    g.set_ylabel("Absolútny počet nehôd",fontsize=30, labelpad=20)
    g.set_xticklabels(get_district_xticklabels(data.index), rotation=90, fontsize=13)
    g.tick_params(axis='y', labelsize=25)
    return encode_plot(fig)

def get_plot_accident_trend_in_county(county_id, start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))
    data = data.loc[data.countyId == county_id]['overallStartTime']
    data = data.map(lambda p: p.date())
    data = data.value_counts().sort_index()
    
    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(25,15))
    plt.title("Vývoj nehôd v čase pre " + d.get_county().loc[county_id]['name'], fontsize=30, pad=20)
    plt.subplots_adjust(left=0.07, right=0.99)
    g = sns.lineplot(x=data.index, y=data.values)
    #g.set_xlabel("Deň",fontsize=30, labelpad=15)
    g.set_ylabel("Počet nehôd",fontsize=30, labelpad=20)
    #g.set_xticklabels(get_date_xtickslabels(data.index), rotation=90, fontsize=20)
    g.tick_params(axis='x', labelsize=25, rotation=45)
    g.tick_params(axis='y', labelsize=25)
    return encode_plot(fig)

def get_plot_accident_trend_in_district(district_id, start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))
    data = data.loc[data.districtId == district_id]['overallStartTime']
    data = data.map(lambda p: p.date())
    data = data.value_counts().sort_index()

    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(25,15))
    plt.title("Vývoj nehôd v čase pre okres " + d.get_district().loc[district_id]['name'], fontsize=30, pad=20)
    plt.subplots_adjust(left=0.07, right=0.99)
    g = sns.lineplot(x=data.index, y=data.values)
    #g.set_xlabel("Deň",fontsize=30, labelpad=15)
    g.set_ylabel("Počet nehôd",fontsize=30, labelpad=20)
    #g.set_xticklabels(get_date_xtickslabels(data.index), rotation=90, fontsize=20)
    g.tick_params(axis='x', labelsize=25, rotation=45)
    g.tick_params(axis='y', labelsize=25)
    return encode_plot(fig)

def get_plot_accident_by_time_in_day(start_datetime=None, end_datetime=None):
    data = d.get_traffic_accident_by_date(get_start_datetime(start_datetime), get_end_datetime(end_datetime))['overallStartTime']
    total_count = data.size
    data = data.map(lambda p: p.time().hour).value_counts().sort_index()
    data = data * 100 / total_count
    
    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(25,15))
    plt.title("Percento nehôd podľa hodiny v dni", fontsize=30, pad=20)
    plt.subplots_adjust(left=0.07, right=0.99)
    g = sns.barplot(x=data.index, y=data.values, palette=get_min_max_colors(data.values))
    g.set_xlabel("Hodina počas dňa",fontsize=30, labelpad=15)
    g.set_ylabel("Percento nehôd",fontsize=30, labelpad=20)
    g.tick_params(axis='x', labelsize=25)
    g.tick_params(axis='y', labelsize=25)
    return encode_plot(fig)
    
def get_date_xtickslabels(index, date_format='%d.%m.'):
    return [x.strftime(date_format) + ' (' + get_short_week_day_name(x.weekday()) + ')' for x in index]

def get_weekday_xtickslabels(index, format='long'):
    fnc = get_long_week_day_name
    if format != 'long':
        fnc = get_short_week_day_name
    return [fnc(x) for x in index]

def get_county_xticklabels(index):
    retval = []
    counties = d.get_county()
    for i in index:
        retval.append(counties.loc[i]['name'])
    return retval

def get_district_xticklabels(index):
    retval = []
    districts = d.get_district()
    for i in index:
        retval.append(districts.loc[i]['name'])
    return retval

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
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    return base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    
#get_plot_accidents_by_county()
#get_plot_total_accidents_by_weekdays()
#get_plot_total_accidents_by_days()
#print(get_start_date(None))
#print(get_end_date(None))