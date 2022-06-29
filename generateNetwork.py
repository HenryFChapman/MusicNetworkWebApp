from pyvis.network import Network
import pandas as pd 
import random
import requests, io


def getMusicianData():
	url = "https://gist.githubusercontent.com/mbejda/9912f7a366c62c1f296c/raw/ae0fed04567e5d8b272aad033cf1f0abadc10766/MTV-10000-Music-Artists.csv"
	download = requests.get(url).content

	# Reading the downloaded content and turning it into a pandas dataframe
	df = pd.read_csv(io.StringIO(download.decode('utf-8')))
	df['name'] = df['name'].str.strip()
	return df

def getColors(musicianDataFrame):

	musicianDataFrame = musicianDataFrame.dropna(subset = ['genre'])

	colorDataFrame = pd.DataFrame()
	colorDataFrame['genre'] = list(set(musicianDataFrame['genre'].tolist()))

	rand_colors = []

	for j in range(len(colorDataFrame.index)):
		tempRand = "#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])
		rand_colors.append(tempRand)

	colorDataFrame['color'] = rand_colors

	return colorDataFrame

def generateNetwork(entireNetwork, musicianDataFrame, queryText):

	colorDataFrame = getColors(musicianDataFrame)

	entireNetwork = entireNetwork[entireNetwork['Original Artist'] != entireNetwork['Affiliated Artist']]

	#Merge In Colors
	entireNetwork = entireNetwork.merge(colorDataFrame,left_on='Original Genre', right_on='genre')
	entireNetwork = entireNetwork.rename(columns={'color': 'Original Color'})
	entireNetwork = entireNetwork[['Affiliated Artist', 'Weight', 'Original Artist', 'Affiliated Genre', "Original Genre", "Original Color"]]

	#Merge In Colors
	entireNetwork = entireNetwork.merge(colorDataFrame,left_on='Affiliated Genre', right_on='genre')
	entireNetwork = entireNetwork.rename(columns={'color': 'Affiliated Color'})
	entireNetwork = entireNetwork[['Affiliated Artist', 'Weight', 'Original Artist', 'Affiliated Genre', "Original Genre", "Original Color", "Affiliated Color"]]

	musicianNetwork = Network(height='100%', width='100%', bgcolor='#FFFFFF', font_color='black')
	musicianNetwork.force_atlas_2based(spring_length=50)

	sources = entireNetwork['Original Artist']
	targets = entireNetwork['Affiliated Artist']
	weight = entireNetwork['Weight']
	originalColor = entireNetwork['Original Color']
	affiliatedColor = entireNetwork['Affiliated Color']
	origialGenre = entireNetwork['Original Genre']
	affiliatedGenre = entireNetwork['Affiliated Genre']

	edge_data = zip(sources, targets, weight, originalColor, affiliatedColor, origialGenre, affiliatedGenre)

	for e in edge_data:
		src = e[0]
		dst = e[1]
		wgt = e[2]
		oc = e[3]
		ac = e[4]
		og = e[5]
		ag = e[6]

		musicianNetwork.add_node(src, src, color = oc, font_size=1000, title=og)
		musicianNetwork.add_node(dst, dst, color = ac, font_size=1000, title = ag)
		musicianNetwork.add_edge(src, dst, value=wgt, color = 'darkgrey', opacity=.1, labelHighlightBold = True)

	neighbor_map = musicianNetwork.get_adj_list()

	# add neighbor data to node hover data
	for node in musicianNetwork.nodes:
		node['title'] += ' Neighbors:<br>' + '<br>'.join(neighbor_map[node['id']])
		node['value'] = len(neighbor_map[node['id']])

	musicianNetwork.set_options("""const options = {
  "nodes": {
    "font": {
      "size": 25
    }
  },
  "physics": {
    "forceAtlas2Based": {
      "springLength": 50,
      "springConstant": 0.205
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based"
  }
}""")

	musicianNetwork.show("assets/" + queryText+'.html')


