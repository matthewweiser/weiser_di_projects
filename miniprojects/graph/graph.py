import pandas as pd
import numpy as np
import os
import re
import datetime
import time
import networkx as nx


df = pd.read_csv( filepath_or_buffer='C:\\Users\\Matt\\Desktop\\nysd_captionData_ALL.txt', sep='\t',  converters={'caption': lambda x: str(x)} )
df.shape

type(df['caption'])
#df = df[ df['caption'].apply(len) < 250 ]
#allCapt = df['caption'].tolist()
allCaptionsBeforeDec = []
for i in range(0, df.shape[0]):
    print df.date[i]
    dateForCapt = time.strptime(df.date[i], " %A, %B %d, %Y ")
    if dateForCapt[0] < 2014 or dateForCapt[1] < 11:
        if len(df.caption[i]) < 250:
            allCaptionsBeforeDec.append(df.caption[i])
len(allCaptionsBeforeDec)   

#now filter using regexpressions:
allCaptionsPhotogRemoved = []
for i in range(0, len(allCaptionsBeforeDec) ):
    if re.search("Photographs by", allCaptionsBeforeDec[i]) == None:
        allCaptionsPhotogRemoved.append(allCaptionsBeforeDec[i])
len(allCaptionsPhotogRemoved)

#split based on titles, commas, etc and then remove leading/trailing white space:
allCaptionsSplit = []
for i in range(0, len(allCaptionsPhotogRemoved) ):
    names_raw = re.split('Mayor |Mrs. |Hon. |Mr. |Dr. |, with | with |, and |, | and ',allCaptionsPhotogRemoved[i])
    name_stripped = []
    for name in names_raw:
        if len(name.split()) > 1 and len(name.split()) < 5:
            single_name_split = name.split()
            #first and last of the names must be capitalized (so as to not punish "de la Rosa", "van der Waal" etc:
            if single_name_split[0][0].isupper() and single_name_split[len(single_name_split)-1][0].isupper():
                name_stripped.append(name.strip())
    allCaptionsSplit.append(name_stripped)
len(allCaptionsSplit)

allCaptionsSplitFinal = []
for i in range(0, len(allCaptionsSplit) ):
    if len(allCaptionsSplit[i]) > 1:
        allCaptionsSplitFinal.append(allCaptionsSplit[i])
len(allCaptionsSplitFinal)


#now you can create the graph and start doing network analysis... 
#format: adjacency matrix? tuples?    

#create list of tuples:
#TEST = [ ['A B', 'R T', 'W C', 'I O' ] ] #allCaptionsSplitFinal
allPairs = []
for i in allCaptionsSplitFinal:
    allNames = i
    for j in range(0, len(allNames)-1 ):
        for k in range(j+1, len(allNames) ):
            allPairs.append(  (allNames[j], allNames[k]) )


G = nx.MultiGraph()
G.add_edges_from(allPairs)
#print G.edges(data=True)
degs = G.degree()
#degs.keys()[0] 
#degs.values()[0] 
degs.items()[0:100] 

##################
# QUESTION 1:
##################
max(degs.values())
max(degs, key=degs.get)
import operator
sorted_degs = sorted(degs.items(), reverse=True, key=operator.itemgetter(1))
sorted_degs[0:100]


##################
# QUESTION 2:
##################
#use this for pagerank:
# make new graph with sum of weights on each edge
H = nx.Graph()
for u,v,d in G.edges(data=True):
    w = 1
    if H.has_edge(u,v):
        H[u][v]['weight'] += w
    else:
        H.add_edge(u,v,weight=w)
#print H.edges(data=True)
pr = nx.pagerank(H, alpha=0.85)
sorted_pr = sorted(pr.items(), reverse=True, key=operator.itemgetter(1))
sorted_pr[0:100]


##################
# QUESTION 3:
##################
weights = H.edges(data='weight')
sorted_weights = sorted(weights, reverse=True, key=lambda tup: tup[2])
sorted_weights[0:100]
sorted_weights2 = []
for i in range(100):
    tup1 = (sorted_weights[i][0], sorted_weights[i][1]) 
    sorted_weights2.append( (tup1,sorted_weights[i][2]) )
sorted_weights2[0:100]    
