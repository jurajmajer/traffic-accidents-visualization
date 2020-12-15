# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 22:08:06 2020

@author: Juraj Majer
"""

from app import app
from app.visualization import plots
from flask import render_template
from flask import Markup
from flask import Response
from flask import request
from datetime import datetime

@app.route('/')
@app.route('/index')
def index():
    start_datetime = plots.get_start_datetime(None)
    end_datetime = plots.get_end_datetime(None)
    return render_template('index.html', plot1=Markup(plots.get_plot_total_accidents_by_days(start_datetime, end_datetime)), plot2=Markup(plots.get_plot_avg_accidents_by_weekdays(start_datetime, end_datetime)),
	plot3=Markup(plots.get_plot_total_accidents_by_county(start_datetime, end_datetime)), plot4=Markup(plots.get_plot_total_accidents_by_district(start_datetime, end_datetime)), 
    plot5=Markup(plots.get_plot_accident_by_time_in_day(start_datetime, end_datetime)), image=Markup(plots.get_plot_total_accidents_by_district(output='json')))

@app.route('/trends')    
def accidents_trends():
    return render_template('trends.html', plot1=Markup(plots.get_plot_accident_trend_in_county(1)), 
                           plot2=Markup(plots.get_plot_accident_trend_in_district(102)))
    
@app.route('/api/figure/total_accidents_by_days')
def get_json_plot_total_accidents_by_days():
    s, e = parse_datetimes()
    return Response(plots.get_plot_total_accidents_by_days(s, e, 'json'), mimetype='application/json')

@app.route('/api/figure/avg_accidents_by_weekdays')
def get_json_plot_avg_accidents_by_weekdays():
    s, e = parse_datetimes()
    return Response(plots.get_plot_avg_accidents_by_weekdays(s, e, 'json'), mimetype='application/json')

@app.route('/api/figure/total_accidents_by_county')
def get_json_plot_total_accidents_by_county():
    s, e = parse_datetimes()
    return Response(plots.get_plot_total_accidents_by_county(s, e, 'json'), mimetype='application/json')

@app.route('/api/figure/total_accidents_by_district')
def get_json_plot_total_accidents_by_district():
    s, e = parse_datetimes()
    return Response(plots.get_plot_total_accidents_by_district(s, e, 'json'), mimetype='application/json')

@app.route('/api/figure/accident_by_time_in_day')
def get_json_plot_accident_by_time_in_day():
    s, e = parse_datetimes()
    return Response(plots.get_plot_accident_by_time_in_day(s, e, 'json'), mimetype='application/json')

def parse_datetimes():
    s = None
    e = None
    if 's' in request.args:
        try:
            s = datetime.strptime(request.args.get('s'), '%d/%m/%Y %H:%M:%S')
        except:
            pass
    if 'e' in request.args:
        try:
            e = datetime.strptime(request.args.get('e'), '%d/%m/%Y %H:%M:%S')
        except:
            pass    
    if s is not None and e is not None and s > e:
        s = None
        e = None    
    return s, e 
    