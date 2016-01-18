Events_2010 <- read.table( "C:/Users/Matt/Desktop/SportsStats/Data/Baseball/GamedayDBTables_InRetrosheetFormat/Events2010_gameday_wSB.txt", sep="\t", header=TRUE, stringsAsFactors=FALSE  )
Events_2011 <- read.table( "C:/Users/Matt/Desktop/SportsStats/Data/Baseball/GamedayDBTables_InRetrosheetFormat/Events2011_gameday_wSB.txt", sep="\t", header=TRUE, stringsAsFactors=FALSE  )
Events_2012 <- read.table( "C:/Users/Matt/Desktop/SportsStats/Data/Baseball/GamedayDBTables_InRetrosheetFormat/Events2012_gameday_wSB.txt", sep="\t", header=TRUE, stringsAsFactors=FALSE  )
Events_2013 <- read.table( "C:/Users/Matt/Desktop/SportsStats/Data/Baseball/GamedayDBTables_InRetrosheetFormat/Events2013_gameday_wSB.txt", sep="\t", header=TRUE, stringsAsFactors=FALSE  )
Events_2014 <- read.table( "C:/Users/Matt/Desktop/SportsStats/Data/Baseball/GamedayDBTables_InRetrosheetFormat/Events2014_gameday_wSB.txt", sep="\t", header=TRUE, stringsAsFactors=FALSE  )
Events <- rbind(Events_2010,Events_2011,Events_2012,Events_2013,Events_2014)

#how to remove the SPs from this?
filter <- Events$HOME_TEAM_ID %in% c("AL", "NL")
sum(filter)
Events <- Events[!filter,]
regularPitchers <- names( table(Events$PIT_ID) )[ table(Events$PIT_ID) > 5 ]
filter <- Events$BAT_LINEUP_ID %in% regularPitchers
sum(filter)
Events <- Events[!filter,]
filter <- Events$BAT_HOME_ID == 0
sum(filter)
Events <- Events[filter,]

#3 =  K
#2 =  Out
#19 = IBB?
#14 = BB?
#20 = 1b
#21 = 2b
#22 = 3b
#23 = HR
filter <- Events$EVENT_CD %in% c(  3, 2, 19, 14,  20, 21, 22, 23 )
Events <- Events[filter,]
allHitterTable <- table( Events$BAT_ID)
allHitters_highSample <- names(allHitterTable)[allHitterTable > 250]

fullTable <- c()
for(i in 1:length(allHitters_highSample)){
  print(i)
  filter <- Events$BAT_ID ==  allHitters_highSample[i]
  subEve <- Events[filter,]
  newRow <- c( sum(subEve$EVENT_CD==3),sum(subEve$EVENT_CD==2)+sum(subEve$EVENT_CD==19),sum(subEve$EVENT_CD==14),
               sum(subEve$EVENT_CD==20),sum(subEve$EVENT_CD==21), sum(subEve$EVENT_CD==22), sum(subEve$EVENT_CD==23)     )
  newRow <- as.numeric(newRow)/ sum(as.numeric(newRow))
  fullTable <- rbind(fullTable, newRow)
}
colnames(fullTable) <- c("Strikeouts", "OutsFromBIP" , "Walk", "Single", "Double", "Triple", "HomeRun")
rownames(fullTable) <-  allHitters_highSample
write.table(fullTable, "HitterStatLines_awayStatsOnly_2010_2014.txt", sep="\t", col.names=NA)


################################################################################
# now feed ths into python and create heatmap as well as a multiclass logistic
# regression with weight assignments for each human...
################################################################################
#example:
import seaborn as sns; sns.set()
import pandas as pd
dat=pd.read_csv( "C:/Users/Matt/Desktop/HitterStatLines_2010_2014.txt",sep="\t",index_col=0)
g = sns.clustermap(dat)
sns.clustermap(dat, standard_scale=1)
sns.clustermap(dat, z_score=1)



