years <- c(2014)
allData <- c()
for(i in 1:length(years) ){
  fileName <- paste( "C:\\Users\\Matt\\Desktop\\dataIncubator\\MLB_proj\\MLB_withDateAndTime_withWeather_", years[i], ".txt", sep=""  )
  #fileName <- paste( "C:\\Users\\Matt\\Desktop\\dataIncubator\\MLB_proj\\MLB_withDateAndTime.txt", sep=""  )
  TMP <- read.table(fileName, sep="\t", header=TRUE, stringsAsFactors=FALSE)
  #TMP$weatherTemp = rnorm(nrow(TMP), 70,15)
  #TMP$weatherDewPt = rnorm(nrow(TMP), 60,8)
  #TMP$weatherHumidity = rnorm(nrow(TMP), 40,30)

  if(i==1){
    allData <- TMP
  } else{
    allData <- rbind(allData, TMP  )
  }
}


#remove teams that play in domes, since weather readings will not be accurate for these (exclude Seattle, since roof is ~always open)
filter <- allData$HomeTeam %in% c( "HOU", "MIA", "TOR", "ARI", "FLA", "FLO", "MIL"  )
allData <- allData[!filter,]

filter <- allData$weatherDewPt == "-"
sum(filter)
allData <- allData[!filter,]
filter <- allData$weatherHumidity == "-"
sum(filter)
allData <- allData[!filter,]
filter <- allData$weatherTemp == "-"
sum(filter)
allData <- allData[!filter,]

allData$weatherDewPt <- as.numeric(allData$weatherDewPt)
allData$weatherTemp <- as.numeric(allData$weatherTemp)
allData$weatherHumidity <- as.numeric(allData$weatherHumidity)

#get mean temperatures and deviation from mean for each of the games:
Totals <-allData$HomeScore + allData$AwayScore
Teams <- unique(allData$HomeTeam)
MeanTemps <- rep(0,length(Teams))
for( i in 1:length(Teams)) {
  MeanTemps[i] <- mean( allData$weatherTemp[ allData$HomeTeam == Teams[i] ] )
}
TeamTemps <- as.data.frame(cbind(Teams, MeanTemps), stringsAsFactors=FALSE)
TeamTemps[,2] <- as.numeric(TeamTemps[,2])
TDiff <- rep(0,nrow(allData))
TDiff_Away <- rep(0, nrow(allData))
for(i in 1:nrow(TeamTemps) ) {
  filter <- allData$HomeTeam == TeamTemps$Teams[i]
  TDiff[filter] <- allData$weatherTemp[filter] - TeamTemps$MeanTemps[i]
  filter <- allData$AwayTeam == TeamTemps$Teams[i]
  TDiff_Away[filter] <-  allData$weatherTemp[filter] - TeamTemps$MeanTemps[i]
}


#do same for humidity:
MeanHumidity <- rep(0,length(Teams))
for( i in 1:length(Teams)) {
  MeanHumidity[i] <- mean(allData$weatherHumidity[ allData$HomeTeam == Teams[i] ] )
}
TeamHumidity <- as.data.frame(cbind(Teams, MeanHumidity), stringsAsFactors=FALSE)
TeamHumidity[,2] <- as.numeric(TeamHumidity[,2])
HumidityDiff <- rep(0,nrow(allData))
HumidityDiff_Away <- rep(0, nrow(allData))
for(i in 1:nrow(TeamTemps) ) {
  filter <- allData$HomeTeam == TeamHumidity$Teams[i]
  HumidityDiff[filter] <- allData$weatherHumidity[filter] - TeamHumidity$MeanHumidity[i]
  filter <- allData$AwayTeam == TeamHumidity$Teams[i]
  HumidityDiff_Away[filter] <-  allData$weatherHumidity[filter] - TeamHumidity$MeanHumidity[i]
}


#and finally for dew point:
MeanDewPt <- rep(0,length(Teams))
for( i in 1:length(Teams)) {
  MeanDewPt[i] <- mean(allData$weatherDewPt[ allData$HomeTeam == Teams[i] ] )
}
TeamDewPt <- as.data.frame(cbind(Teams, MeanDewPt), stringsAsFactors=FALSE)
TeamDewPt[,2] <- as.numeric(TeamDewPt[,2])
DewPtDiff <- rep(0,nrow(allData))
DewPtDiff_Away <- rep(0, nrow(allData))
for(i in 1:nrow(TeamTemps) ) {
  filter <- allData$HomeTeam == TeamDewPt$Teams[i]
  DewPtDiff[filter] <- allData$weatherDewPt[filter] - TeamDewPt$MeanDewPt[i]
  filter <- allData$AwayTeam == TeamDewPt$Teams[i]
  DewPtDiff_Away[filter] <-  allData$weatherDewPt[filter] - TeamDewPt$MeanDewPt[i]
}


length( Teams )

jpeg("parkTempDistributions.jpeg")
par(mfrow=c(5,5) )
par(mar=c(2.1, 1.1, 1.1, 1.1))
for( i in 1:25 ){
  filter <- allData$HomeTeam == Teams[i]
  dat <- allData$weatherTemp[filter]
  plot( density(dat) , main=paste(Teams[i], "Temp"), xlim=c(30,120), xlab="" , col="red")
}
dev.off()

jpeg("parkHumidityDistributions.jpeg")
par(mfrow=c(5,5) )
par(mar=c(2.1, 1.1, 1.1, 1.1))
for( i in 1:25 ){
  filter <- allData$HomeTeam == Teams[i]
  dat <- allData$weatherHumidity[filter]
  plot( density(dat) , main=paste(Teams[i], "Humidity"), xlim=c(30,120), xlab="" , col="blue")
}
dev.off()

jpeg("parkDewPtDistributions.jpeg")
par(mfrow=c(5,5) )
par(mar=c(2.1, 1.1, 1.1, 1.1))
for( i in 1:25 ){
  filter <- allData$HomeTeam == Teams[i]
  dat <- allData$weatherDewPt[filter]
  plot( density(dat) , main=paste(Teams[i], "DewPt"), xlim=c(30,120), xlab="" , col="blue")
}
dev.off()


#look at pearson correlation of weaher variables (deviation from average) with run scoring:
cor_temp <- cor( TDiff, Totals )
cor_humidity <- cor( HumidityDiff, Totals )
cor_dew <- cor( DewPtDiff, Totals )
jpeg("weatherEfectsOnScoring.jpeg")
barplot( c(  cor_temp, cor_humidity, cor_dew ), names=c("cor_temp", "cor_humidity", "cor_dew"   ), ylab="Correlation with run scoring" )
dev.off()

































































































