# run this on command line:
#cd ~/notebookScratch/sql/nyc_inspection_data
#iconv   -f utf-8   -t utf-8  -c -o  Action_converted.txt   Action.txt  
#iconv   -f utf-8   -t utf-8  -c -o  WebExtract_converted.txt   WebExtract.txt  
#iconv   -f utf-8   -t utf-8  -c -o  Borough_converted.txt   Borough.txt  
#iconv   -f utf-8   -t utf-8  -c -o  Cuisine_converted.txt   Cuisine.txt  
#iconv   -f utf-8   -t utf-8  -c -o  Violation_converted.txt   Violation.txt  


import re
import sys
import sqlite3
import os
import sqlalchemy
import pandas as pd
import sql
from sqlalchemy.engine import create_engine
import datetime
import numpy as np 
from scipy import stats



#replace problematic fields:
infile=open("/home/vagrant/notebookScratch/sql/nyc_inspection_data/Violation_converted.txt", 'r')
outfile=open("/home/vagrant/notebookScratch/sql/nyc_inspection_data/Violation_converted_clean.txt", 'w')
for line in infile:
    #print line
    line = re.sub(r'([^"]),([^"])', r'\1;\2', line)
    outfile.write(line)            
outfile.close()    
  
#create empt db:
engine = create_engine('sqlite:///sqdb/nycInspectionData.db')
connection = engine.connect()

#read data and create db tables:
violations=pd.read_csv('nyc_inspection_data/Violation_converted_clean.txt',low_memory=False)
grades=pd.read_csv('nyc_inspection_data/WebExtract_converted.txt',low_memory=False)
boroughs=pd.read_csv('nyc_inspection_data/Borough_converted.txt',low_memory=False)
actions=pd.read_csv('nyc_inspection_data/Action_converted.txt',low_memory=False)
cuisines=pd.read_csv('nyc_inspection_data/Cuisine_converted.txt',low_memory=False)

with sqlite3.connect('sqdb/nycInspectionData.db') as con:
    violations.to_sql('violations',con,flavor='sqlite', if_exists='replace'   )
    actions.to_sql('actions',con,flavor='sqlite', if_exists='replace'    )
    cuisines.to_sql('cuisines',con,flavor='sqlite', if_exists='replace'   )
    violations.to_sql('violations',con,flavor='sqlite', if_exists='replace'   )
    grades.to_sql('grades', con, flavor='sqlite', if_exists='replace'   )
    boroughs.to_sql('boroughs',con,flavor='sqlite', if_exists='replace'   )
con.close()


#convert dates to a sortable format and srt the df:
grades=pd.read_csv('nyc_inspection_data/WebExtract_converted.txt',low_memory=False)
DATE=[datetime.datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S' ) for date in grades.INSPDATE ]
print DATE[:6]
grades['DATE'] = DATE
grades = grades.sort("DATE", ascending=False)





#######################################
# Question 1:
#######################################
uniqueZips = set(grades.ZIPCODE)
print uniqueZips

def isNotNan(x):
    return x==x

allCommonZipScores = []
for uz in uniqueZips:
    subGrades = grades[ grades['ZIPCODE']==uz ]
    uniqueRestsForZip = set(subGrades['CAMIS'])
    if len(uniqueRestsForZip) > 100:
        print len(uniqueRestsForZip)  
        allLatestScores = []
        for ur in uniqueRestsForZip:
            thisRestGrades = subGrades[ subGrades['CAMIS']==ur ]
            thisRestGrades = thisRestGrades[ map(isNotNan , thisRestGrades['SCORE'] )  ]
            if thisRestGrades.shape[0] > 0:
                #print type(thisRestGrades.SCORE[0])
                #print type(thisRestGrades['SCORE'][0])
                allLatestScores.append( thisRestGrades.iloc[0,11] )   
                print thisRestGrades.iloc[0,11]           
        allCommonZipScores.append( (str(int(uz)), np.mean(allLatestScores), stats.sem(allLatestScores), len(uniqueRestsForZip)  )    )  #len(uniqueRestsForZip)
                
print(len(allCommonZipScores))
allCommonZipScores_sorted = sorted(allCommonZipScores, key=lambda x: x[1])
print allCommonZipScores_sorted


#######################################
# Question 2:
#######################################
df = pd.DataFrame(allCommonZipScores_sorted, columns=['ZIP', 'MEAN', 'SDE', 'NUMREST'])
print df.shape
df.to_csv('restGradingsTableForMapVis.csv', index=False)






#######################################
# Question 3:
#######################################
df = pd.DataFrame(allCommonZipScores_sorted, columns=['ZIP', 'MEAN', 'SDE', 'NUMREST'])
import sqlite3
def isNotNan(x):
    return x==x

db_filename = 'sqdb/nycInspectionData.db'
with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()       
    q="select  grades.CAMIS, grades.SCORE, grades.BORO, grades.ZIPCODE, grades.INSPDATE, boroughs.BOROSTRING from grades INNER JOIN boroughs ON boroughs.BORONUM = grades.BORO"
    df = pd.read_sql_query(q, conn)
    #print df.head()
    #print df.shape
    # grades.shape
    
    DATE=[datetime.datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S' ) for date in df.INSPDATE ]
    df['DATE'] = DATE    
    df = df.sort("DATE", ascending=False)
    
    df_clean = df[ df['BORO'] != 0 ]
    #df_clean.fillna(0, inplace=True)
    allBoroString = set(df_clean.BOROSTRING)
    allBoroScores = []
    for b in allBoroString:
        subGrades = df_clean[ df_clean['BOROSTRING']==b ]
        uniqueRestsForBoro = set(subGrades['CAMIS'])        
        if len(uniqueRestsForBoro) > 100:
            print len(uniqueRestsForBoro) 
            allLatestScores = []
            for ur in uniqueRestsForBoro:
                thisRestGrades = subGrades[ subGrades['CAMIS']==ur ]
                #thisRestGrades = thisRestGrades[ map(isNotNan , thisRestGrades['SCORE'] )  ]
                #thisRestGrades.fillna(0, inplace=True)
                if thisRestGrades.shape[0] > 0 and map(isNotNan , thisRestGrades['SCORE'] )[0] == True:
                    allLatestScores.append( thisRestGrades.iloc[0,1] )  
                    #print thisRestGrades.iloc[0,1]   
            allBoroScores.append( ( b   , np.mean(allLatestScores), stats.sem(allLatestScores), len(uniqueRestsForBoro) )   )
allBoroScores_sorted = sorted(allBoroScores, key=lambda x: x[1])
print allBoroScores_sorted

#######################################
# Question 4:
#######################################
def isNotNan(x):
    return x==x

db_filename = 'sqdb/nycInspectionData.db'
with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()
        
    q="select  grades.CAMIS, grades.SCORE, grades.CUISINECODE, grades.INSPDATE, grades.VIOLCODE, cuisines.CODEDESC from grades INNER JOIN cuisines ON cuisines.CUISINECODE = grades.CUISINECODE"
    df = pd.read_sql_query(q, conn)
    print df.head()
    print df.shape
    # grades.shape
    allCuisines =set(df.CODEDESC) 
    print len(allCuisines)
    
    vioPerCuisine = []
    for c in allCuisines:
        #print df[df['CODEDESC']==c].shape[0]
        subTable = df[df['CODEDESC']==c]
        if df[df['CODEDESC']==c].shape[0] >= 100:
            #get the scores:
            subTable = subTable[ map(isNotNan , subTable['SCORE'] )  ]
            scores = subTable.SCORE          
            vioPerCuisine.append(  (c,  np.mean(scores), stats.sem(scores) , df[df['CODEDESC']==c].shape[0]  )      )
    print len(vioPerCuisine)
vioPerCuisine_sorted = sorted(vioPerCuisine, key=lambda x: x[1])
print vioPerCuisine_sorted 





#######################################
# Question 5:
#######################################
def isNotNan(x):
    return x==x
def isGreaterThanSetDate(x):
    cutoffDate = datetime.datetime(2014, 1, 1)
    return x > cutoffDate

db_filename = 'sqdb/nycInspectionData.db'
with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()
    q="select * from violations"
    df_viol = pd.read_sql_query(q, conn)    
    DATE=[datetime.datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S' ) for date in df_viol.ENDDATE ]    
    df_viol_recent = df_viol[ map(isGreaterThanSetDate, DATE )  ]
    q="select  grades.CAMIS, grades.SCORE, grades.CUISINECODE, grades.INSPDATE, grades.VIOLCODE, cuisines.CODEDESC from grades INNER JOIN cuisines ON cuisines.CUISINECODE = grades.CUISINECODE"
    df_grades = pd.read_sql_query(q, conn)
    print df_grades.head()
    print df_grades.shape   
    TMP = pd.merge(df_grades, df_viol_recent, how='inner', left_on='VIOLCODE', right_on='VIOLATIONCODE')

#create hash table storing number of tmes ech cuisine/violation pair are found,
#so we can look at only those for the enrichment scores by cuisine:    
import collections
pairsOfHighSampleSize=[]
uniqueCuisines = set(TMP.CODEDESC)
uniqueViols = set(TMP.VIOLATIONDESC)
ids = TMP['CODEDESC'] + "XXXXXXX" + TMP['VIOLATIONDESC']
cnt = collections.Counter()
for pair in ids:
    cnt[pair] += 1

highSampleSizePairs = []
for key, value in cnt.iteritems():
    if value >= 100:
        keys_1_2 = key.split("XXXXXXX")
        highSampleSizePairs.append(( keys_1_2[0] , keys_1_2[1], value ))
highSampleSizePairs
print len(highSampleSizePairs)   

 print TMP.shape
print df_grades.shape
uniqueCuisines = set(TMP.CODEDESC)
uniqueViols = set(TMP.VIOLATIONDESC)
allPairData = []
ctr=0


#also get a hsh table for number of entries per cuisine- will save time later!
cnt_cuisine = collections.Counter()
for c in TMP.CODEDESC:
    cnt_cuisine[c] += 1
    
#now get ratios for the pairs that have > 100 instances:
for p in highSampleSizePairs:    
    c=p[0]
    v=p[1]
    print ctr
    ctr+=1
    dataForCuisineAndViolPair = p[2] #TMP[ (TMP['CODEDESC']==c) & (TMP['VIOLATIONDESC']==v)  ]
    numInstancesOfCuisine = cnt_cuisine[c]
    dataForViol = TMP[TMP['VIOLATIONDESC']==v ]          
    #now get the normalized ratio:
    condProb = dataForCuisineAndViolPair / float(numInstancesOfCuisine)            
    uncondProb = dataForViol.shape[0] / float(TMP.shape[0] )
    ratio = condProb / uncondProb
    print ratio           
    allPairData.append(   ( ( c, v  ), ratio, dataForCuisineAndViolPair.shape[0] )   )
pairs_sorted = sorted(allPairData, key=lambda x: x[1], reverse=True)
print pairs_sorted[:20]
     
     















