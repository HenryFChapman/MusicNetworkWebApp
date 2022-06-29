import requests
import urllib.parse
import json
import pandas as pd
import sys
import os
import io
from generateNetwork import generateNetwork
import time 
from pathlib import Path


#Query Function that sends a Get Request to the Infegy API
def getQuery(endpoint, queryString, limit):
	text_file = open("api.txt", "r")
	key = text_file.read()
	text_file.close()
	#key = "9dWTcTFzvUoir0Ox21QGOcIjSsVLv66A"
	url = "https://atlas.infegy.com/api/v3/" + endpoint + "?api_key=" + key +  "&limit=" + str(limit) + "&q="+ queryString

	data = requests.get(url).json()
	time.sleep(2)
	return data

#Calling Function that Identifies a query + target endpoint and returns a dataframe
def getData(query, targetEndpoint, limit):
	query = urllib.parse.quote(str(json.dumps(query, indent = 4)))
	data = getQuery(targetEndpoint, query, limit)

	testData = pd.DataFrame.from_dict(data['output'])
	if len(testData.index) == 0:
		return testData

	testData = testData.sort_values(by=['documents'], ascending = False)
	return testData

#Grabs the Musician Dataset downloaded from Github and puts in into a data frame/cleans it. 

def getMusicianData():
	url = "https://gist.githubusercontent.com/mbejda/9912f7a366c62c1f296c/raw/ae0fed04567e5d8b272aad033cf1f0abadc10766/MTV-10000-Music-Artists.csv"
	download = requests.get(url).content

	# Reading the downloaded content and turning it into a pandas dataframe
	df = pd.read_csv(io.StringIO(download.decode('utf-8')))
	df['name'] = df['name'].str.strip()
	return df


def filterByMusicianData(originalData, musicianDataFrame):

	excludeList = pd.read_csv("excludeList.csv")
	excludeList = list(set(excludeList['ExcludeList'].tolist()))
	listOfArtists = musicianDataFrame['name'].tolist()
	filteredArtists = originalData[originalData['name'].isin(musicianDataFrame['name'].tolist())]
	filteredArtists = filteredArtists[~filteredArtists['name'].isin(excludeList)]

	return filteredArtists

def createQuery(queryText, dateRange):

	query = {
	  "query": queryText,
	  "query_fields": ["body","title"],
	  "analyze_fields": ["body","title"],
	  "filter": [{
		"id": "published",
		"min": dateRange,
		"max": "now"
	   },{
    "id": "language",
    "value": "en"
   	}],
	  "group_by": "day",
	  "group_on": "published"
	 }

	return query

def main(queryText):

	print(queryText)
	query = createQuery(queryText, dateRange)

	originalData  = getData(query, 'entities', 50)

	if len(originalData.index) == 0:
		return


	musicianDataFrame = getMusicianData()
	filteredArtists = filterByMusicianData(originalData, musicianDataFrame)

	networkCreation = pd.DataFrame()
	networkCreation['Affiliated Artist'] = filteredArtists['name'].tolist()
	networkCreation['Weight'] = filteredArtists['appearances'].tolist()
	networkCreation['Original Artist'] = queryText 

	networkList = [networkCreation]

	for artist in filteredArtists['name'].tolist():
		
		print("*****" +artist)
		tempNetworkDataFrame = pd.DataFrame()
		query = createQuery(artist.replace('"', ''), dateRange)
		originalData  = getData(query, 'entities', 50)

		if len(originalData.index) == 0:
			continue

		filteredArtists = filterByMusicianData(originalData, musicianDataFrame)

		tempNetworkDataFrame['Affiliated Artist'] = filteredArtists['name'].tolist()
		tempNetworkDataFrame['Weight'] = filteredArtists['appearances'].tolist()
		tempNetworkDataFrame['Original Artist'] = artist

		networkList.append(tempNetworkDataFrame)

	entireNetwork = pd.concat(networkList)
	entireNetwork = entireNetwork.merge(musicianDataFrame[['name','genre']],left_on='Affiliated Artist', right_on='name')
	entireNetwork = entireNetwork.rename(columns={'genre': 'Affiliated Genre'})
	entireNetwork = entireNetwork[['Affiliated Artist', 'Weight', 'Original Artist', 'Affiliated Genre']]

	entireNetwork = entireNetwork.merge(musicianDataFrame[['name','genre']],left_on='Original Artist', right_on='name')
	entireNetwork = entireNetwork.rename(columns={'genre': 'Original Genre'})
	entireNetwork = entireNetwork[['Affiliated Artist', 'Weight', 'Original Artist', 'Affiliated Genre', "Original Genre"]]

	entireNetwork.to_csv("EntireNetwork.csv")

	generateNetwork(entireNetwork, musicianDataFrame, queryText)

dateRange = "3 years ago"

musicianData = getMusicianData()
musicianData = musicianData['name'].str.replace(r'[^\w\s]', '').tolist()

for mus in musicianData:
	my_file = Path("assets/"+mus+".html")
	if my_file.is_file():
		print("Skipping " + mus)
		continue
	else:
		main(mus)
		time.sleep(5)
