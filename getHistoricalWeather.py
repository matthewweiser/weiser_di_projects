import pandas as pd
import numpy as np
import os
import urllib2
import re
from BeautifulSoup import BeautifulSoup

def extractYear(date):
    return str(int(str(date)[0:4]))

def isTimeLater(time1Full, time2Full):
    time1 = time1Full.split()[0]
    amOrPm1 = time1Full.split()[1]  
    hour1 = int(time1.split(':')[0])   
    min1 = int(time1.split(':')[1]) 
    if amOrPm1 == 'PM' and hour1 != 12:
        hour1 = hour1 + 12   
    time2 = time2Full.split()[0]
    amOrPm2 = time2Full.split()[1]        
    hour2 = int(time2.split(':')[0])   
    min2 = int(time2.split(':')[1])  
    if amOrPm2 == 'PM' and hour2 != 12:
        hour2 = hour2 + 12         
    if( amOrPm1 == 'PM' and amOrPm2 == 'AM'):
        return True
    elif( amOrPm1 == 'AM' and amOrPm2 == 'PM'): 
        return False
    elif( amOrPm1 == amOrPm2 and hour1 > hour2 ): 
        return True
    elif( amOrPm1 == amOrPm2 and hour1 < hour2 ): 
        return False
    elif( amOrPm1 == amOrPm2 and hour1 == hour2 and min1 >= min2 ): 
        return True
    elif( amOrPm1 == amOrPm2 and hour1 == hour2 and min1 < min2 ): 
        return False
    else: 
        print "FORMAT ERROR IN TIMES"
        return False


#import bs4
hdr = {'User-Agent':'Mozilla/5.0'}
baseUrl = 'http://www.wunderground.com/history/airport/'
#homePageUrl = 'http://www.wunderground.com/history/airport/KORD/2013/1/28/DailyHistory.html?&reqdb.zip=&reqdb.magic=&reqdb.wmo=&MR=1'
#homePageUrl = 'http://www.wunderground.com/history/airport/KCQT/2015/11/11/DailyHistory.html'

#TEST- initialize on the index page:
#homePageRequest =urllib2.Request(homePageUrl,headers=hdr)
#homePage =urllib2.urlopen(homePageRequest)
#homePageHTML = BeautifulSoup(homePage)
#currentPage = homePageHTML

# for visualization of the actual tag structure:
#Html_file= open("C:\\Users\\Matt\\Desktop\\TEST.txt","w")
#Html_file.write(str(currentPage))
#Html_file.close()

df = pd.read_csv( filepath_or_buffer='C:\\Users\\Matt\\Desktop\\dataIncubator\\MLB_proj\\MLB_withDateAndTime.txt', sep='\t', low_memory=False )
df.shape
#df.dtypes.index
dateOnly = df.Date        
yr = dateOnly.apply(extractYear)
df = df[ yr=='2014' ]
#df = df[2:10]
#df.index.values
df.index = range(df.shape[0])

dfloc = pd.read_csv( filepath_or_buffer='C:\\Users\\Matt\\Desktop\\dataIncubator\\MLB_proj\\parkToCodeMap.txt', sep='\t', low_memory=False )
dfloc.shape


weatherTime = []
weatherTemp = []
weatherDewPt = []
weatherHumidity = []
weatherPressure = []
weatherWindDir = []
weatherWindSpeed = []
weatherPrecip = []

ctr = 0
for i in range(0, df.shape[0] ):
    print ctr
    ctr = ctr + 1
    print df.Date[i]
    ind = dfloc[ dfloc['HomeTeam'] == df.HomeTeam[i] ].index.tolist()[0]
    code = dfloc.get_value(ind, 'WeatherCode')   
    year = str(int(str(df.Date[i])[0:4]))
    month = str(int(str(df.Date[i])[4:6]))
    day = str(int(str(df.Date[i])[6:8]))
    url = baseUrl + code + '/' + year + '/' + month + '/' + day + '/DailyHistory.html'
    pageRequest =urllib2.Request(url,headers=hdr)
    page =urllib2.urlopen(pageRequest)
    pageHTML = BeautifulSoup(page)
    currentPage = pageHTML
    
    ele = currentPage.findAll('tr', attrs={'class':'no-metars'} )
    foundCorrectRow = False

    #ele.findAll('td' )
    for subEle in ele:
        #extract time, determine if this time is later then game time, break loop if it is
        timeFull = subEle.findNext().text
        time = timeFull.split()[0] + ':00'
        amOrPm = timeFull.split()[1]  
        gameTime = df.allTimes[i] + ' ' + df.allAMPM[i]       
        if isTimeLater(timeFull, gameTime): 
            break
            
    colElements =  subEle.findAll('td')  
    if len(colElements)==13: 
        weatherTime.append(  colElements[0].text  )
        weatherTemp.append( colElements[1].text.split(';')[0].replace('&nbsp','') )
        weatherDewPt.append( colElements[3].text.split(';')[0].replace('&nbsp','') )
        weatherHumidity.append( colElements[4].text.split(';')[0].replace('%','') )
        weatherPressure.append( colElements[5].text.split(';')[0].replace('&nbsp','') )
        weatherWindDir.append( colElements[7].text.split(';')[0].replace('&nbsp','') )
        weatherWindSpeed.append( colElements[8].text.split(';')[0].replace('&nbsp','') )
        weatherPrecip.append( colElements[10].text.split(';')[0].replace('&nbsp','') )
    if len(colElements)==12: 
        weatherTime.append(  colElements[0].text  )
        weatherTemp.append( colElements[1].text.split(';')[0].replace('&nbsp','') )
        weatherDewPt.append( colElements[2].text.split(';')[0].replace('&nbsp','') )
        weatherHumidity.append( colElements[3].text.split(';')[0].replace('%','') )
        weatherPressure.append( colElements[4].text.split(';')[0].replace('&nbsp','') )
        weatherWindDir.append( colElements[6].text.split(';')[0].replace('&nbsp','') )
        weatherWindSpeed.append( colElements[7].text.split(';')[0].replace('&nbsp','') )
        weatherPrecip.append( colElements[9].text.split(';')[0].replace('&nbsp','') )


df['weatherTime'] = weatherTime
df['weatherTemp'] = weatherTemp
df['weatherDewPt'] = weatherDewPt
df['weatherHumidity'] = weatherHumidity
df['weatherPressure'] = weatherPressure
df['weatherWindDir'] = weatherWindDir
df['weatherWindSpeed'] = weatherWindSpeed
df['weatherPrecip'] = weatherPrecip
df.to_csv( path_or_buf='C:\\Users\\Matt\\Desktop\\dataIncubator\\MLB_proj\\MLB_withDateAndTime_withWeather_2014.txt', sep='\t', index=False , encoding='utf-8' )

#df = pd.read_csv( filepath_or_buffer='C:\\Users\\Matt\\Desktop\\beerAdvocateData_ALL_WITHDATE_CONVERTED.txt', sep='\t' )
#userIDs = df['user']
#for u in uniqueUserIDs:



