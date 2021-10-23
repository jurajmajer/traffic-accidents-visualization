# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 21:00:08 2021

@author: Juraj Majer
"""
#TODO: validate if token is really valid and somebody does not want to DDOS us
from app.data import models as m
from app import db

import json
import datetime

def save_subscription(data):
    parsed_data = parse_data(data)
    
    item = m.WebPushNotification(
            token_id=parsed_data['token']['endpoint'], 
            token=json.dumps(parsed_data['token']),
            monday=parsed_data['weekdays'][0],
            tuesday=parsed_data['weekdays'][1],
            wednesday=parsed_data['weekdays'][2],
            thursday=parsed_data['weekdays'][3],
            friday=parsed_data['weekdays'][4],
            saturday=parsed_data['weekdays'][5],
            sunday=parsed_data['weekdays'][6],
            from_time=parse_time(parsed_data['from_time'] + ':00'),
            to_time=parse_time(parsed_data['to_time'] + ':59')
            )
    db.session.add(item)
    db.session.flush()
    
    for county_id in parsed_data['counties']:
        if county_id is None:
            continue
        db.session.add(m.WebPushNotificationLocation(
                webpushnotification_id=item.id,
                county_id=county_id
                ))
    for district_id in parsed_data['districts']:
        if district_id is None:
            continue
        db.session.add(m.WebPushNotificationLocation(
                webpushnotification_id=item.id,
                district_id=district_id
                ))
    
    db.session.commit()

def remove_subscription(data):
    parsed_token = parse_data(data)["token"]
    item = m.WebPushNotification.query.filter(m.WebPushNotification.token_id == parsed_token['endpoint']).first()
    if item is not None:
        m.WebPushNotificationLocation.query.filter(m.WebPushNotificationLocation.webpushnotification_id == item.id).delete()
        db.session.delete(item)
        db.session.commit()
    
def parse_data(data):
    if len(data) > 1024:
        raise ValueError('Data length is too long')
    retval = json.loads(data)
    if 'endpoint' not in retval["token"] or 'keys' not in retval["token"]:
        raise ValueError('Token is invalid: ' + retval["token"])
    return retval

def parse_time(time_str):
    return datetime.datetime.strptime(time_str, '%H:%M:%S').time()