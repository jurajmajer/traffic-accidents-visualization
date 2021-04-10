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

def get_counties_in_groups(num_in_one_group):
    df = d.get_county()
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