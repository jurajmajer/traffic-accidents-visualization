# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 22:03:18 2020

@author: Juraj Majer
"""

from timeit import default_timer as t

perf_time_start = 0

def perf_start():
    global perf_time_start
    perf_time_start = t()
    
def perf_lap(msg = None):
    global perf_time_start
    if msg is not None:
        msg += " "
    else:
        msg = ""
    end = t()
    msg += str((end - perf_time_start))
    perf_time_start = end
    print(msg)
    