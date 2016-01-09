from urlparse import urljoin
from bs4 import BeautifulSoup
import requests
from collections import namedtuple
import pandas as pd

CaptionContainer = namedtuple('CaptionContainer', 'partyName, date, url, caption')
baseUrl = 'http://www.newyorksocialdiary.com/'
allCaptionInfo =[]

for pageNum in range(27):
    #print pageNum
    response = requests.get( urljoin(baseUrl, 'party-pictures'), params={"page": pageNum})
    print response.url    
    soup = BeautifulSoup(response.text)

    allTitles = soup.select('div.view-content span.views-field-title')#.select('a')[0]
    allDates = soup.select('div.view-content span.views-field-created')#.select('a')[0]
    for title, date in zip(allTitles, allDates):
        partyTitle = title.select('a')[0].text.encode('ascii', 'ignore').decode('ascii') #title.text
        partyUrl = title.select('a')[0]['href'].encode('ascii', 'ignore').decode('ascii')
        partyDate = date.text.encode('ascii', 'ignore').decode('ascii')
        #print partyTitle
        #print urljoin(baseUrl, partyUrl)      
        #print partyDate
    
        #now navigate to this party's url and grab all the captions:
        partyPage = requests.get(urljoin(baseUrl, partyUrl) ) 
        partySoup = BeautifulSoup(partyPage.text)   
        allCaptions1 = partySoup.select('.photocaption')
        if len(allCaptions1) != 0:
            for capt1 in allCaptions1:
                if capt1.text != '': allCaptionInfo.append(CaptionContainer(partyName=partyTitle, date=partyDate, url=partyUrl, caption=capt1.text.encode('ascii', 'ignore').decode('ascii').replace('\n','').replace('\t','')  ))                     
        allCaptions2 = partySoup.select('font')
        if len(allCaptions2) != 0:
            for capt2 in allCaptions2:
                if capt2.text != '': allCaptionInfo.append(CaptionContainer(partyName=partyTitle, date=partyDate, url=partyUrl, caption=capt2.text.encode('ascii', 'ignore').decode('ascii').replace('\n','').replace('\t','') ))                                      
    print len(allCaptionInfo)
    
    
    
    
len(allCaptionInfo)
df = pd.DataFrame(allCaptionInfo, columns=CaptionContainer._fields)
CaptionContainer._fields
df[1:100]
df.to_csv('nysd_captionData_ALL.txt', sep='\t', encoding='utf-8')

