# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 22:08:06 2020

@author: Juraj Majer
"""

from app import app
from app.visualization import plots
from flask import render_template
from flask import Markup

@app.route('/')
@app.route('/index')
def index():
    start_datetime = plots.get_start_datetime(None)
    end_datetime = plots.get_end_datetime(None)
    return render_template('index.html', plot1=Markup(plots.get_plot_total_accidents_by_days(start_datetime, end_datetime)), plot2=Markup(plots.get_plot_avg_accidents_by_weekdays(start_datetime, end_datetime)),
	plot3=Markup(plots.get_plot_total_accidents_by_county(start_datetime, end_datetime)), plot4=Markup(plots.get_plot_total_accidents_by_district(start_datetime, end_datetime)), 
    plot5=Markup(plots.get_plot_accident_by_time_in_day(start_datetime, end_datetime)))

@app.route('/trends')    
def accidents_trends():
    return render_template('trends.html', plot1=Markup(plots.get_plot_accident_trend_in_county(1)), 
                           plot2=Markup(plots.get_plot_accident_trend_in_district(102)))
    