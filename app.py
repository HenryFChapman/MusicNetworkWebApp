import flask
import pandas as pd
import requests
import io
import dash
import dash_html_components as html
from dash import dcc
from dash.dependencies import Output, Input
import os 


from flask import Flask, request, render_template

#def grabListPopulation():
#	url = "https://gist.githubusercontent.com/mbejda/9912f7a366c62c1f296c/raw/ae0fed04567e5d8b272aad033cf1f0abadc10766/MTV-10000-Music-Artists.csv"
#	download = requests.get(url).content

	# Reading the downloaded content and turning it into a pandas dataframe
#	df = pd.read_csv(io.StringIO(download.decode('utf-8')))

#	df = df.sort_values(by='name')
#	df = df.dropna(subset = 'name')
#	df['name'] = df['name'].str.replace('"', '')
#	available_indicators = df['name'].unique()

#	return available_indicators


def grabListPopulation():
    assetList = os.listdir("assets")

    return assetList

available_indicators = grabListPopulation()

app = dash.Dash()
app.layout = html.Div(
    [
        dcc.Dropdown(
        	id="input",
			options=[{'label': i.split(".html")[0], 'value': i} for i in available_indicators],
            value="TheRollingStones.html",
            multi=False,
            placeholder="Enter a band or an artist.",
        ),

        html.Iframe(
            id="my-output",
            src="TheRollingStones.html",
            style={"height": "800px", "width": "100%"},
        ),
    ]
)


@app.callback(
    Output("my-output", "src"), Input("input", "value"), prevent_initial_call=False)


def update_output_div(input_value):
    return f"assets/{input_value}"

if __name__ == "__main__":
    app.run_server()