#!/usr/bin/env python
'''
slimweather - Quick easy script to grab data from weather station and publish to wunderground.

Change variables below (e.g. ID, PASSWORD, & ROOTDIR for your wunderground account and your specific system)
'''
########################################################### 
# Release 1.0  - 9/1/2013 - Jeremy Georges - Initial Script
# 
##########################################################

import pycurl, time, urllib, os, pickle
import cStringIO
#import pywws.WeatherStation
from pywws import WeatherStation
# Dependancy - pywws
# http://jim-easterbrook.github.io/pywws/doc/en/html/index.html 

def main():
  ws = WeatherStation.weather_station()
  #print ws.get_fixed_block()

  #Make sure you have trailing /
  ROOTDIR='/pub/vault/weather/'
  RAINDATA='RAINDATA.pickle'
  pressure_offset=.48
  # Grab raw current output

  #We should see 'success' in this file if everything uploads to wunderground ok.
  STATUSFILE=ROOTDIR +'wgetfile.log'

  # Necessary Variables
  #============================================================
  # Need to parse this data and create variables for uploading to wunderground
  ID='MyStationID'
  PASSWORD='mypassword'

  THEEPOCHTIME=str(int(round(time.time(), 0)))
  CURRENTTIME=time.strftime("%Y-%m-%d+%T", time.gmtime())
  WEBTIME=urllib.pathname2url(CURRENTTIME)

  #print ws.get_data(ws.current_pos(), unbuffered=False)

  #Create blank dictionary and then copy this from current buffer from WeatherStation.
  currentdata={}
  currentdata = ws.get_data(ws.current_pos(), unbuffered=False) 

  #get_data gives us a dictionary back. Here are the keys to work with
  #'hum_out': 97, 'wind_gust': 0, 'wind_ave': 0, 'rain': 167.7, 'temp_in': 28.900000000000002, 'delay': 0, 'abs_pressure': 1008.8000000000001, 'hum_in': 37, 'temp_out': 12.200000000000001, 'wind_dir': 14

  #=======================================================
  # UNIT CONVERSION 
  #======================================================
  #Now lets convert some of these key/value pairs to a unit that Wunderground uses.
  #Convert Windgust from m/s to MPH
  currentdata['wind_gust']=round(float(currentdata['wind_gust']) * 2.237,1)

  #Convert Wind Speed from m/s to MPH
  currentdata['wind_ave']=round(float(currentdata['wind_ave']) * 2.237, 1)

  #Convert from C to fahrenheit 
  currentdata['temp_in']=round(float(currentdata['temp_in']) * 1.8 + 32, 1)
  currentdata['temp_out']=round(float(currentdata['temp_out']) * 1.8 + 32, 1)

  #Convert RAINTOTAL from mm to inches
  currentdata['rain']=int(currentdata['rain']) * 0.039370

  #Convert barometer from hPa to inches
  currentdata['abs_pressure']=(float(currentdata['abs_pressure']) * 0.0295) + pressure_offset

  # Calculate dewpoint
  # Td = T - ((100 - RH)/5.)   Td is dewpoint, T in celsius 

  DEWPOINT=float(currentdata['temp_out']) - 9/25 * (100 - int(currentdata['hum_out']))
  #TD: =243.04*(LN(RH/100)+((17.625*T)/(243.04+T)))/(17.625-LN(RH/100)-((17.625*T)/(243.04+T))) 

  #Convert wind_dir integer which is 0-16 by 22.5 to give degrees.
  currentdata['wind_dir']=float(currentdata['wind_dir']) * 22.5

  #=====================================================
  # Rain Calculations
  #====================================================
  #RAIN LOGIC. Wunderground wants hourly rainfall, not total which is provided from the weather station.
  # We need to save the total at an hourly period, save epoch time (in seconds) and then we add up the delta for the hourly rollup.
  #Then at the next hour or (3600 seconds), we zero out the hourly and take another total rainfall snapshot.


  if os.path.exists(ROOTDIR + RAINDATA) == True:
       #Create dictionarys to store previous stats and unpack these via pickle file
       raindata={}
       with open(ROOTDIR+RAINDATA, "rb") as dictionaryfh:
         try:
           raindata = pickle.load(dictionaryfh)
         except:
           print "Pickle load had an exception. Going to have to go with current stats as starting point."
           #If the pickle file is bad, then we'll start over like the file doesn't exist 
           raindata['HOURLYSNAPSHOT']= THEEPOCHTIME
           raindata['RAINHOURLY']=currentdata['rain']
           raindata['MIDNIGHTSNAPSHOT']=currentdata['rain']
           RAINDELTA=0
           DAILYRAINTOTAL=0
       dictionaryfh.close()

       #add rain logic here
       #here we'll set RAINDELTA and DAILYTOTAL values
       if int(THEEPOCHTIME) - int(raindata['HOURLYSNAPSHOT']) >= 3600:
        #We need to redo snapshot for our hourly
        raindata['HOURLYSNAPSHOT']= THEEPOCHTIME
        raindata['RAINHOURLY']=currentdata['rain']
        RAINDELTA=0
       else:
         RAINDELTA=float(currentdata['rain']) - float(raindata['RAINHOURLY'])
     
       #Check for midnight
       # Lets also run through a test to see if we need to update the 'dailyrain' value.
       # This we need to take a snapshot at midnight of total rainfall. Then we will do a delta throughout the day based on the snapshot.
       # The idea is, if we're running this script every minute, then we'll land at midnight (since we're not grep'ing on seconds) at least once.
       # If we change the script execution time, then this isn't going to work correctly. If its set under 60 seconds, then we'll just reset a few times
       # which should not be a BIG issue. The likely hood of the rain numbers incrementing much in a few seconds at midnight is very unlikely and
       # I don't think we're going for that kind of accuracy.
      
       #grab time. Then strip out the seconds. Since we're just checking to see if we're at midnight 
       checktime=time.strftime("%T", time.localtime()).split(':')
       timenoseconds=checktime[0] + ':' + checktime[1] 
       if timenoseconds == '00:00':
         print "Its midnight"
         #Starting over since its midnight
         raindata['MIDNIGHTSNAPSHOT'] = float(currentdata['rain'])
         DAILYRAINTOTAL=0

       else:
         print "its NOT midnight" 
         DAILYRAINTOTAL=float(currentdata['rain']) - float(raindata['MIDNIGHTSNAPSHOT']) 


  else:
      print "No pickle file found. Initial run assumed."
      raindata={}
      raindata['HOURLYSNAPSHOT']= THEEPOCHTIME
      raindata['RAINHOURLY']=currentdata['rain']
      raindata['MIDNIGHTSNAPSHOT']=currentdata['rain']
      RAINDELTA=0
      DAILYRAINTOTAL=0 
    

  #Lets dump our dictionary for next run
  with open (ROOTDIR+RAINDATA, 'wb') as dictionaryfh:
    pickle.dump((raindata), dictionaryfh)
  dictionaryfh.close()




  #We need to replicate this:
  #Maybe pycurl or urllib?
  #wget -O$STATUSFILE "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?ID=$ID&PASSWORD=$PASSWORD&dateutc=$THETIME&winddir=$WINDDIR&windspeedmph=$WINDSPEEDM&windgustmph=$WINDGUSTM&tempf=$TEMPF&rainin=$RAINDELTA&dailyrainin=$DAILYTOTAL&baromin=$BAROINCHES&dewptf=$DEWPOINTF&humidity=$OUTHUMIDITY&weather=&clouds=&softwaretype=vws%20versionxx&action=updateraw"

  buf = cStringIO.StringIO()
  #Set various variables for URL to make it a little more manageable as a string
  WURL='http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?' 
  AUTH='ID=' + ID + '&' + 'PASSWORD=' + PASSWORD + '&'
  THETIME='dateutc=' + WEBTIME + '&'
  WINDIR='winddir=' + str(currentdata['wind_dir']) + '&'
  WINDSPEED='windspeedmph=' + str(currentdata['wind_ave']) + '&'
  WINDGUST='windgustmph=' + str(currentdata['wind_gust']) + '&'
  TEMP='tempf=' + str(currentdata['temp_out']) + '&'
  RAININ='rainin=' + str(RAINDELTA) + '&' #add variable here
  DAILYRAIN='dailyrainin=' + str(DAILYRAINTOTAL) + '&' 

  BARO='baromin=' + str(currentdata['abs_pressure']) + '&'
  DEW='dewptf=' + str(DEWPOINT) + '&'
  HUM='humidity=' + str(currentdata['hum_out']) + '&' 
  TRAILER="weather=&clouds=&softwaretype=vws%20versionxx&action=updateraw"

  c = pycurl.Curl()
  c.setopt(c.URL, WURL + AUTH + THETIME + WINDIR + WINDSPEED + WINDGUST + TEMP + RAININ + DAILYRAIN + BARO + DEW + HUM + TRAILER)
  c.setopt(c.WRITEFUNCTION, buf.write)
  c.perform()

  #Print output from wunderground 
  print "Sending the following URL: "
  print WURL + AUTH + THETIME + WINDIR + WINDSPEED + WINDGUST + TEMP + RAININ + DAILYRAIN + BARO + DEW + HUM + TRAILER
  print "Returned value: ", buf.getvalue()


  #Print to log file
  with open(ROOTDIR + 'weather.log','w') as rawfile:
     print >> rawfile, "Sending the following URL: ", WURL + AUTH + THETIME + WINDIR + WINDSPEED + WINDGUST + TEMP + RAININ + DAILYRAIN + BARO + DEW + HUM + TRAILER, "   Returned value: ", buf.getvalue() 
  rawfile.close()
  buf.close()


if __name__ == "__main__":
   main()

