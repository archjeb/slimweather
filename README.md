# slimweather - A Small, Simple, Data pull from a weather station and Push to Wunderground

Written by Jeremy Georges 

Release 1.0

## Dependencies
* [pywws][id]
    [id] http://jim-easterbrook.github.io/pywws/doc/en/html/index.html "pywws" 
* Ambient Weather Station -  WS-2080

## Description
The reason for me writing this script, is because much of the weather station software was really heavy. They require
a database to store weather station information, and in many cases required some level of storage requirements. The previous station I had required a Windows App and so I had a VM running constantly to pull the data and 
then push it to wunderground. In reality, I never looked at the data stored with the windows app...I would just
log in to wunderground and look at my stored data there. So when I purchased the WS-2080, I wanted a simpler 
script to run that I could potentially move over to a Beaglebone board, or Raspberry Pi. (I'm still running
it on an x86 platform, I just wanted the option if I ever wanted to move to a smaller platform).
     
I wanted something simple that would keep track of rainfall and just store it using the pickle module as
wunderground only wants rainfall numbers for the last 24 hours. Everything else, I just want to upload it 
to wunderground and leverage the data store there (such as the station history). I didn't want to store that locally. 

The general idea is to run this script in cron every minute, and the script pulls the last data block in memory 
parse/convert to the appropriate unit of measurement and then upload to wunderground. Additionally, it stores
the rainfall data in the RAINDATA.pickle file. We clear the rainfall data at midnight, since that is when
wunderground begins the rainfall count. 


## Installation

* Install pywws from http://jim-easterbrook.github.io/pywws/doc/en/html/index.html 
* Open slimweather.py and change the variables:
  * ID (This is your wunderground station ID)
  * PASSWORD (This is your wunderground password)
  * ROOTDIR (This is where you want to execute slimweather.py  and store the weather station data)

* You can also use the quickget.py to make sure you can communicate with your weather station. This will 
grab the last block of data stored on your weather station. 
 

