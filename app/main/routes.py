# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 22:08:06 2020

@author: Juraj Majer
"""

from app import app
from app.visualization import plots
from app.visualization import maps
from app.visualization import viz_utils as vu
from flask import render_template
from flask import Markup
from flask import Response
from flask import request, send_from_directory
from datetime import datetime
from dateutil.relativedelta import relativedelta

@app.route('/')
@app.route('/index')
def index():
    s, e = parse_datetimes()
    return render_template('index.html', 
                           start_date=s.strftime("%Y-%m-%d"),
                           end_date=e.strftime("%Y-%m-%d"),
                           plot1=Markup(plots.get_plot_total_accidents_by_days(s, e, 'json')), 
                           plot2=Markup(plots.get_plot_avg_accidents_by_weekdays(s, e, 'json')),
                           plot3=Markup(plots.get_plot_total_accidents_by_county(s, e, 'json')), 
                           plot4=Markup(plots.get_plot_total_accidents_by_district(s, e, 'json')), 
                           plot5=Markup(plots.get_plot_accident_by_time_in_day(s, e, 'json')),
                           plot6=Markup(plots.get_plot_total_accidents_by_city(s, e, 'json')))

@app.route('/trends')    
def accidents_trends():
    return render_template('trends.html', plot1=Markup(plots.get_plot_accident_trend_in_county(1)), 
                           plot2=Markup(plots.get_plot_accident_trend_in_district(102)))
    
@app.route('/district')
def district():
    s, e = parse_datetimes()
    return render_template('district.html',
                           start_date=s.strftime("%Y-%m-%d"),
                           end_date=e.strftime("%Y-%m-%d"),
                           choropleth_map=Markup(maps.get_district_choropleth(s, e)),
                           plot1=Markup(plots.get_plot_total_accidents_by_district(s, e, 'json'))
                           )

@app.route('/district_detail/<district_id>')
def district_detail(district_id):
    district_id = int(district_id)
    s, e = parse_datetimes()
    return render_template('district_detail.html',
                           start_date=s.strftime("%Y-%m-%d"),
                           end_date=e.strftime("%Y-%m-%d"),
                           district_name = vu.get_district_name(district_id),
                           district_id = district_id,
                           detail_map=Markup(maps.get_district_detail_map(district_id, s, e)),
                           accident_trend_bar_plot=Markup(plots.get_plot_accident_trend_in_district(district_id, s, e))
                           )
    
@app.route('/county')
def county():
    s, e = parse_datetimes()
    return render_template('county.html',
                           start_date=s.strftime("%Y-%m-%d"),
                           end_date=e.strftime("%Y-%m-%d"),
                           choropleth_map=Markup(maps.get_county_choropleth(s, e)),
                           plot1=Markup(plots.get_plot_total_accidents_by_county(s, e, 'json'))
                           )

@app.route('/county_detail/<county_id>')
def county_detail(county_id):
    county_id = int(county_id)
    s, e = parse_datetimes()
    return render_template('county_detail.html',
                           start_date=s.strftime("%Y-%m-%d"),
                           end_date=e.strftime("%Y-%m-%d"),
                           county_name = vu.get_county_name(county_id),
                           county_id = county_id,
                           detail_map=Markup(maps.get_county_detail_map(county_id, s, e)),
                           accident_trend_bar_plot=Markup(plots.get_plot_accident_trend_in_county(county_id, s, e))
                           )
    
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

@app.route('/api/figure/total_accidents_by_city')
def get_json_plot_total_accidents_by_city():
    s, e = parse_datetimes()
    return Response(plots.get_plot_total_accidents_by_city(s, e, 'json'), mimetype='application/json')

@app.route('/api/figure/accident_trend_in_county/<county_id>')
def get_json_plot_accident_trend_in_county(county_id):
    county_id = int(county_id)
    s, e = parse_datetimes()
    return Response(plots.get_plot_accident_trend_in_county(county_id, s, e, 'json'), mimetype='application/json')

@app.route('/api/figure/accident_trend_in_district/<district_id>')
def get_json_plot_accident_trend_in_district(district_id):
    district_id = int(district_id)
    s, e = parse_datetimes()
    return Response(plots.get_plot_accident_trend_in_district(district_id, s, e, 'json'), mimetype='application/json')

@app.route('/api/map/district_detail_map/<district_id>')
def get_map_district_detail(district_id):
    district_id = int(district_id)
    s, e = parse_datetimes()
    return Response(maps.get_district_detail_map(district_id, s, e, 'json'), mimetype='application/json')

@app.route('/api/map/county_detail_map/<county_id>')
def get_map_county_detail(county_id):
    county_id = int(county_id)
    s, e = parse_datetimes()
    return Response(maps.get_county_detail_map(county_id, s, e, 'json'), mimetype='application/json')

@app.route('/api/map/choropleth_district')
def get_map_choropleth_district():
    s, e = parse_datetimes()
    return Response(maps.get_district_choropleth(s, e, 'json'), mimetype='application/json')
    
@app.route('/api/map/choropleth_county')
def get_map_choropleth_county():
    s, e = parse_datetimes()
    return Response(maps.get_county_choropleth(s, e, 'json'), mimetype='application/json')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

def parse_datetimes():
    s = None
    e = None
    if 's' in request.args:
        try:
            s = datetime.strptime(request.args.get('s'), '%Y-%m-%d')
            s = s.replace(hour=0, minute=0, second=0, microsecond=0)
        except:
            pass
    if 'e' in request.args:
        try:
            e = datetime.strptime(request.args.get('e'), '%Y-%m-%d')
            e = e.replace(hour=23, minute=59, second=59, microsecond=999999)
        except:
            pass    
    if s is not None and e is not None and s > e:
        s = None
        e = None
    now = datetime.now()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if s is not None and s >= now:
        s = None
    if e is not None and e >= now:
        e = None
    if e is None:
        e = datetime.now() - relativedelta(days=1)
        e = e.replace(hour=23, minute=59, second=59, microsecond=999999)
    if s is None:
        s = e - relativedelta(days=30)
        s = s.replace(hour=0, minute=0, second=0, microsecond=0)
    return s, e 
