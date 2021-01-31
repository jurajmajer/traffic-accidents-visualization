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
    
    def __repr__(self):
        return '<TrafficAccidents {}>'.format(self.overallStartTime)
    