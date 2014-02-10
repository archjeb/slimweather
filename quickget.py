#!/usr/bin/env python
'''
Quick grab of weather station data to make sure communication is working properly
'''

#Dependency is pywws package
# http://jim-easterbrook.github.io/pywws/doc/en/html/index.html

from pywws import WeatherStation


ws = WeatherStation.weather_station()
print "Fixed block data: "
print '=' * 70
print ws.get_fixed_block()

print "Current data: " 
print '=' * 70
print ws.get_data(ws.current_pos(), unbuffered=False)

