# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 22:57:49 2020

@author: Juraj Majer
"""

from app import db

class County(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return '<County {}>'.format(self.name) 
    
class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    
    def __repr__(self):
        return '<District {}>'.format(self.name)
    
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    
    def __repr__(self):
        return '<City {}>'.format(self.name)
    
class TrafficAccident(db.Model):
    __tablename__ = 'trafficaccidents'
    
    id = db.Column(db.Integer, primary_key=True)
    sourceName = db.Column(db.String(128), nullable=True)
    overallStartTime = db.Column(db.DateTime, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    countyId = db.Column(db.Integer, nullable=True)
    districtId = db.Column(db.Integer, nullable=True)
    cityId = db.Column(db.Integer, nullable=True)
    roadNumber = db.Column(db.String(32), nullable=True)
    roadPosition = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return '<TrafficAccidents {}>'.format(self.overallStartTime)
    
class NearbyAccident(db.Model):
    __tablename__ = 'nearbyaccidents'
    
    id = db.Column(db.Integer, primary_key=True)
    accident1_id = db.Column(db.Integer, nullable=False)
    accident2_id = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return '<NearbyAccident {}, {}, {}>'.format(self.accident1_id, self.accident2_id, self.distance)
    
class Road(db.Model):
    __tablename__ = 'skroadnetwork'
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(16), nullable=True)
    classification = db.Column(db.Integer, nullable=True)
    direction = db.Column(db.Integer, nullable=True)
    shape_length = db.Column(db.Integer, nullable=True)
    shape = db.Column(db.String(100000), nullable=True)
    
    def __repr__(self):
        return '<Road {}, {}, {}, {}>'.format(self.number, self.classification, self.direction, self.shape_length)
    
class WebPushNotification(db.Model):
    __tablename__ = 'webpushnotification'
    
    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(512), nullable=False)
    monday = db.Column(db.Boolean, nullable=False)
    tuesday = db.Column(db.Boolean, nullable=False)
    wednesday = db.Column(db.Boolean, nullable=False)
    thursday = db.Column(db.Boolean, nullable=False)
    friday = db.Column(db.Boolean, nullable=False)
    saturday = db.Column(db.Boolean, nullable=False)
    sunday = db.Column(db.Boolean, nullable=False)
    from_time = db.Column(db.Time, nullable=False)
    to_time = db.Column(db.Time, nullable=False)
    
    def __repr__(self):
        return '<token_id {}>'.format(self.token_id)
    
class WebPushNotificationLocation(db.Model):
    __tablename__ = 'webpushnotificationlocation'
    
    id = db.Column(db.Integer, primary_key=True)
    webpushnotification_id = db.Column(db.Integer, db.ForeignKey("webpushnotification.id", ondelete='CASCADE'))
    county_id = db.Column(db.Integer, nullable=True)
    district_id = db.Column(db.Integer, nullable=True)
    roadNumber = db.Column(db.String(32), nullable=True)
    from_roadPosition = db.Column(db.Float, nullable=True)
    to_roadPosition = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return '<webpushnotification_id {}>'.format(self.webpushnotification_id)
    
    