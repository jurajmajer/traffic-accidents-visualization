# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 21:35:32 2021

@author: Juraj Majer
"""

from app.data import datasource as d
import re

def get_district_name(district_id):
    names = d.get_district()
    return names.loc[district_id]['name']

def get_county_name(county_id):
    names = d.get_county()
    return names.loc[county_id]['name']

def get_county_id_for_district(district_id):
    return int(district_id / 100)
    
def get_counties_in_groups(num_in_one_group):
    return form_groups(d.get_county(), 4)

def get_districts_in_groups(county_id, num_in_one_group):
    df = d.get_district()
    df = df.loc[df.index >= county_id*100]
    df = df.loc[df.index < (county_id+1)*100]
    return form_groups(df, 4)

def get_districts_in_groups_by_county(num_in_one_group):
    df = d.get_county()
    retval = []
    for i,row in df.iterrows():
        retval.append([row['name'], get_districts_in_groups(i, 4)])
    return retval
    
def form_groups(df, num_in_one_group):
    retval = []
    group = []
    temp = 0
    for index, row in df.iterrows():
        if temp == num_in_one_group:
            retval.append(group)
            group = []
            temp = 0
        group.append((index, row['name']))
        temp += 1
    if temp > 0:
        retval.append(group)
    return retval

def key_func(e):
    e = re.sub('\D', '', e)
    return int(e)

def get_roads_by_classification(classification):
    retval = d.get_road()
    retval = retval.loc[retval.direction == 1]
    retval = retval[retval['classification'].isin(classification)]
    retval = retval['number'].tolist()
    retval.sort(key=key_func)
    return retval

def get_all_roads_list():
    retval = []
    highways = []
    speedways = []
    temp = get_roads_by_classification([0,6])
    for t in temp:
        if t.startswith('R'):
            speedways.append(t)
        else:
            highways.append(t)
    retval.append(['Diaľnice a diaľničné privádzače', highways])
    retval.append(['Rýchlostné cesty', speedways])
    retval.append(['Cesty I. triedy', get_roads_by_classification([1])])
    retval.append(['Cesty II. triedy', get_roads_by_classification([2])])
    retval.append(['Cesty III. triedy', get_roads_by_classification([3])])
    return retval

def get_road(road_number):
    retval = d.get_road()
    retval = retval.loc[retval.direction == 1]
    retval = retval.loc[retval.number == road_number]
    return retval.iloc[0]
    