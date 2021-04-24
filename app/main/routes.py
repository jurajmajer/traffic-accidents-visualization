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
from flask import request, send_from_directory, make_response
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import g
from timeit import default_timer as t
from app.main import utils as u
import locale

locale.setlocale(locale.LC_ALL, 'sk_SK.utf8')
MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS = 20

@app.before_request
def before_request():
    g.start = t()

@app.after_request
def after_request(response):
    diff = t() - g.start
    print(request.path + ': ' + str(diff) + 's')
    return response

@app.route('/')
@app.route('/index')
def index():
    s, e = parse_datetimes(u.get_min_date(), u.get_max_date())
    tmpl = render_template('index.html', 
                           title='Štatistika dopravných nehôd v Slovenskej republike',
                           page_title='Štatistika dopravných nehôd v Slovenskej republike', 
                           frequent_accidents_map=Markup(maps.get_map_with_most_frequent_accidents_for_country(MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS, s, e)),
                           accident_trend_bar_plot=Markup(plots.get_plot_total_accident_trend(s, e, 'json')), 
                           **get_date_kwargs(s, e),
                           **get_general_kwargs('home')
                           )
    return set_date_cookie(make_response(tmpl))

@app.route('/stats')
def stats():
    s, e = parse_datetimes()
    tmpl = render_template('stats.html', 
                           title='Zaujímavé štatistiky',
                           page_title='Zaujímavé štatistiky',                           
                           plot1=Markup(plots.get_plot_avg_accidents_by_weekdays(s, e, 'json')), 
                           plot2=Markup(plots.get_plot_accident_by_time_in_day(s, e, 'json')),
                           plot3=Markup(plots.get_plot_total_accidents_by_city(s, e, 'json')),
                           **get_date_kwargs(s, e),
                           **get_general_kwargs('stats')
                           )
    return set_date_cookie(make_response(tmpl))
    
@app.route('/district')
def district():
    s, e = parse_datetimes()
    tmpl = render_template('district.html',
                           title='Prehľad dopravných nehôd podľa okresov',
                           page_title='Prehľad dopravných nehôd podľa okresov',
                           choropleth_map=Markup(maps.get_district_choropleth(s, e)),
                           total_accidents_by_district_plot=Markup(plots.get_plot_total_accidents_by_district(s, e, 'json')),
                           **get_date_kwargs(s, e),
                           **get_general_kwargs('district'),
                           district_groups=vu.get_districts_in_groups_by_county(4)
                           )
    return set_date_cookie(make_response(tmpl))

@app.route('/district_detail/<district_id>')
def district_detail(district_id):
    district_id = int(district_id)
    district_name = vu.get_district_name(district_id)
    s, e = parse_datetimes()
    tmpl = render_template('district_detail.html',
                           **get_date_kwargs(s, e),
                           **get_general_kwargs(None),
                           title='Prehľad dopravných nehôd v okrese ' + district_name,
                           page_title='Prehľad dopravných nehôd v okrese ' + district_name,
                           district_name = district_name,
                           district_id = district_id,
                           frequent_accidents_map=Markup(maps.get_map_with_most_frequent_accidents_for_district(district_id, MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS, s, e)),
                           accident_trend_bar_plot=Markup(plots.get_plot_accident_trend_in_district(district_id, s, e)),
                           district_groups=vu.get_districts_in_groups(vu.get_county_id_for_district(district_id), 4)
                           )
    return set_date_cookie(make_response(tmpl))
    
@app.route('/county')
def county():
    s, e = parse_datetimes()
    tmpl = render_template('county.html',
                           title='Prehľad dopravných nehôd podľa krajov',
                           page_title='Prehľad dopravných nehôd podľa krajov',
                           **get_date_kwargs(s, e),
                           **get_general_kwargs('county'),
                           choropleth_map=Markup(maps.get_county_choropleth(s, e)),
                           total_accidents_by_county_plot=Markup(plots.get_plot_total_accidents_by_county(s, e, 'json')),
                           county_groups=vu.get_counties_in_groups(4)
                           )
    return set_date_cookie(make_response(tmpl))

@app.route('/county_detail/<county_id>')
def county_detail(county_id):
    county_id = int(county_id)
    county_name = vu.get_county_name(county_id)
    s, e = parse_datetimes()
    tmpl = render_template('county_detail.html',
                           **get_date_kwargs(s, e),
                           **get_general_kwargs(None),
                           title='Prehľad dopravných nehôd pre ' + county_name,
                           page_title='Prehľad dopravných nehôd pre ' + county_name,
                           county_name = county_name,
                           county_id = county_id,
                           frequent_accidents_map=Markup(maps.get_map_with_most_frequent_accidents_for_county(county_id, MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS, s, e)),
                           accident_trend_bar_plot=Markup(plots.get_plot_accident_trend_in_county(county_id, s, e)),
                           district_groups=vu.get_districts_in_groups(county_id, 4)
                           )
    return set_date_cookie(make_response(tmpl))
    
@app.route('/road')
def road():
    s, e = parse_datetimes()
    tmpl = render_template('road.html',
                           title='Prehľad dopravných nehôd podľa ciest',
                           page_title='Prehľad dopravných nehôd podľa ciest',
                           **get_date_kwargs(s, e),
                           **get_general_kwargs('road'),
                           plot1=Markup(plots.get_plot_total_accidents_by_roads(s, e, 50, 'json')),
                           plot2=Markup(plots.get_plot_total_accidents_ratio_by_roads(s, e, 50, 'json')),
                           road_list=vu.get_all_roads_list()
                           )
    return set_date_cookie(make_response(tmpl))

@app.route('/road_detail/<road_number>')
def road_detail(road_number):
    s, e = parse_datetimes()
    tmpl = render_template('road_detail.html',
                           title='Prehľad dopravných nehôd pre cestu ' + road_number,
                           page_title='Prehľad dopravných nehôd pre cestu ' + road_number,
                           **get_date_kwargs(s, e),
                           **get_general_kwargs(None),
                           road_number = road_number,
                           frequent_accidents_map=Markup(maps.get_map_with_most_frequent_accidents_for_road(road_number, MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS, s, e)),
                           accident_trend_bar_plot=Markup(plots.get_plot_accident_trend_on_road(road_number, s, e))
                           )
    return set_date_cookie(make_response(tmpl))
    
@app.route('/api/figure/total_accident_trend')
def get_json_plot_total_accidents_by_days():
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_total_accident_trend(s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/avg_accidents_by_weekdays')
def get_json_plot_avg_accidents_by_weekdays():
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_avg_accidents_by_weekdays(s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/total_accidents_by_county')
def get_json_plot_total_accidents_by_county():
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_total_accidents_by_county(s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/total_accidents_by_district')
def get_json_plot_total_accidents_by_district():
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_total_accidents_by_district(s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/accident_by_time_in_day')
def get_json_plot_accident_by_time_in_day():
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_accident_by_time_in_day(s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/total_accidents_by_city')
def get_json_plot_total_accidents_by_city():
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_total_accidents_by_city(s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/accident_trend_in_county/<county_id>')
def get_json_plot_accident_trend_in_county(county_id):
    county_id = int(county_id)
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_accident_trend_in_county(county_id, s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/accident_trend_in_district/<district_id>')
def get_json_plot_accident_trend_in_district(district_id):
    district_id = int(district_id)
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_accident_trend_in_district(district_id, s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/accident_trend_on_road/<road_number>')
def get_json_plot_accident_trend_on_road(road_number):
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_accident_trend_on_road(road_number, s, e, 'json'), mimetype='application/json'))

@app.route('/api/figure/road/total_accident_by_road')
def get_json_plot_total_accidents_by_road():
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_total_accidents_by_roads(s, e, 50, 'json'), mimetype='application/json'))

@app.route('/api/figure/road/total_accident_ratio_by_road')
def get_json_plot_total_accidents_ratio_by_road():
    s, e = parse_datetimes()
    return set_date_cookie(Response(plots.get_plot_total_accidents_ratio_by_roads(s, e, 50, 'json'), mimetype='application/json'))

@app.route('/api/map/district_detail_map/<district_id>')
def get_map_district_detail(district_id):
    district_id = int(district_id)
    s, e = parse_datetimes()
    return set_date_cookie(Response(maps.get_district_detail_map(district_id, s, e, 'json'), mimetype='application/json'))

@app.route('/api/map/county_detail_map/<county_id>')
def get_map_county_detail(county_id):
    county_id = int(county_id)
    s, e = parse_datetimes()
    return set_date_cookie(Response(maps.get_county_detail_map(county_id, s, e, 'json'), mimetype='application/json'))

@app.route('/api/map/road_detail_map/<road_number>')
def get_map_road_detail(road_number):
    s, e = parse_datetimes()
    return set_date_cookie(Response(maps.get_map_with_most_frequent_accidents_for_road(road_number, MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS, s, e, 'json'), mimetype='application/json'))

@app.route('/api/map/choropleth_district')
def get_map_choropleth_district():
    s, e = parse_datetimes()
    return set_date_cookie(Response(maps.get_district_choropleth(s, e, 'json'), mimetype='application/json'))
    
@app.route('/api/map/choropleth_county')
def get_map_choropleth_county():
    s, e = parse_datetimes()
    return set_date_cookie(Response(maps.get_county_choropleth(s, e, 'json'), mimetype='application/json'))

@app.route('/api/map/district/frequent_accidents/<district_id>')
def get_map_district_frequent_accidents(district_id):
    district_id = int(district_id)
    s, e = parse_datetimes()
    return set_date_cookie(Response(maps.get_map_with_most_frequent_accidents_for_district(district_id, MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS, s, e, 'json'), mimetype='application/json'))

@app.route('/api/map/county/frequent_accidents/<county_id>')
def get_map_county_frequent_accidents(county_id):
    county_id = int(county_id)
    s, e = parse_datetimes()
    return set_date_cookie(Response(maps.get_map_with_most_frequent_accidents_for_county(county_id, MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS, s, e, 'json'), mimetype='application/json'))

@app.route('/api/map/country/frequent_accidents')
def get_map_country_frequent_accidents():
    s, e = parse_datetimes()
    return set_date_cookie(Response(maps.get_map_with_most_frequent_accidents_for_country(MAX_NUMBER_OF_MOST_FREQUEST_ACCIDENTS, s, e, 'json'), mimetype='application/json'))

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

def get_general_kwargs(navlink_active):
    retval = {
                'current_year': datetime.now().year
             }
    if navlink_active is not None:
        retval['nav_link_'+navlink_active+'_active'] = ' w3-blue'
    return retval

def get_date_kwargs(s, e):
    retval = {
                'min_date':u.get_min_date().strftime("%Y-%m-%d"),
                'max_date':u.get_max_date().strftime("%Y-%m-%d"),
                'start_date':s,
                'end_date':e
              }
    return retval

def parse_datetimes(default_start=None, default_end=None):
    s = None
    e = None
    s, e = parse_datetimes_from_query_string()
    if s is None and e is None:
        s = default_start
        e = default_end
    if s is None and e is None:
        s, e = parse_datetimes_from_cookie()
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
        e = u.get_max_date()
    if s is None:
        s = e - relativedelta(days=30)
        s = s.replace(hour=0, minute=0, second=0, microsecond=0)
    return s, e

def get_datetime_from_string(string, round_up):
    try:
        retval = datetime.strptime(string, '%Y-%m-%d')
        if round_up:
            retval = retval.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            retval = retval.replace(hour=0, minute=0, second=0, microsecond=0)
    except:
        return None
    return retval

def parse_datetimes_from_query_string():
    s = None
    e = None
    if 's' in request.args:
        s = get_datetime_from_string(request.args.get('s'), False)
    if 'e' in request.args:
        e = get_datetime_from_string(request.args.get('e'), True)
    return s, e

def parse_datetimes_from_cookie():
    s = None
    e = None
    if 'start_date' in request.cookies:
        s = get_datetime_from_string(request.cookies.get('start_date'), False)
    if 'end_date' in request.cookies:
        e = get_datetime_from_string(request.cookies.get('end_date'), True)
    return s, e

def set_date_cookie(response):
    s = None
    e = None
    s, e = parse_datetimes_from_query_string()
    if s is None or e is None:
        return response
    response.set_cookie('start_date', request.args.get('s'))
    response.set_cookie('end_date', request.args.get('e'))
    return response
