# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 22:49:58 2020

@author: Juraj Majer
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False