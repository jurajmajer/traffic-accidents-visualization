# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 21:35:32 2021

@author: Juraj Majer
"""

from app.data import datasource as d

def get_district_name(district_id):
    names = d.get_district()
    return names.loc[district_id]['name']

def get_county_name(county_id):
    names = d.get_county()
    return names.loc[county_id]['name']

def get_county_id_for_district(district_id):
    return district_id / 100;
    
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