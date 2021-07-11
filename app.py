import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import geojson
import random
import numpy as np
from vis_elements.control import Controls 
from dash.dependencies import Input, Output

country_codes = pd.read_csv('./country-codes-europe.csv')
stations_europe = pd.read_csv('./stations-europe.csv')
temperature_monthly = pd.read_csv('./temperature-monthly-europe.csv')


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


controls = Controls.get_controls()



fig_euro_map = go.Figure(data=go.Choropleth(locations=list(country_codes.Name),
                locationmode = 'country names',
                colorscale= 'RdBu',
                reversescale=True,
                text=country_codes.Code,
                customdata=country_codes.Code,
                marker_line_color='White',
                z=['0', '0', '0', '0', '0', '0', '0', '0', '0']),
               layout=dict(geo = {'scope':'europe'}))
fig_euro_map.update_layout(title="Country View")
fig_euro_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
fig_euro_map.update_layout(clickmode='event+select')

fig_euro_line = go.Figure()
fig_euro_line.update_layout(title="Country Readings")
fig_euro_line.update_layout(xaxis_title="Date",
    yaxis_title="Temperature")
fig_country_line = go.Figure()
fig_country_line.update_layout(title="Station Readings")
fig_country_line.update_layout(xaxis_title="Date",
    yaxis_title="Temperature")



def get_country_map(ccode): 
    with open("./geojson/" + ccode + ".geojson", "r", encoding="utf-8") as f:
        geometry = geojson.load(f)

    ids = []
    for i in range(len(geometry['features'])): 
        ids.append(geometry['features'][i]['properties']['id'])
    z = []
    for i in range(len(ids)): 
        z.append(random.randint(0,0))

    stations = stations_europe.loc[stations_europe['CountryCode'] == ccode]

    fig = go.Figure(data=go.Choropleth(geojson = geometry,showscale=False, locations=ids, featureidkey='properties.id',z=z,hoverinfo='text', colorscale=[[0, 'rgb(176,213,230)'], [1,'rgb(176,213,230)']]))
    fig.update_layout(coloraxis_showscale=False)


    fig.add_trace(
        go.Scattergeo(
            name = "",
            customdata = stations['Station'],
            lon = stations['Longitude'],
            lat = stations['Latitude'],
            text = stations['Station'] + " "  + stations['Name'] + " " + stations['Elevation'].astype(str)+"m",
            mode = 'markers', 
            marker = dict(
                size = 12,
                opacity = 0.8,
            )
    ))

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    fig.update_layout(clickmode='event+select')
    fig.update_layout(title="Station View")

    return fig

#Inits
fig_country_map = get_country_map("SW")


app.layout = dbc.Container(
    [
        html.H4("Assignment 3 - Temperature Dataset"),
        html.H5("by Matus Maruna (MM223FJ)"),
        html.Hr(),
        dbc.Row(
            [
            
            dbc.Col([
            dbc.Row(
                [
                    dbc.Col(controls, width={"size": 3}),
                    dbc.Col(dbc.Card(dcc.Graph(id="euromap", figure=fig_euro_map))),
                    dbc.Col(dbc.Card(dcc.Graph(id="countrymap", figure=fig_country_map))),
                ],
                align="top",
            ),
            dbc.Row(
                [
                   dbc.Col(dbc.Card(dcc.Graph(id="euroline", figure=fig_euro_line))), 
                   dbc.Col(dbc.Card(dcc.Graph(id="countryline", figure=fig_country_line))),

                ],
                align="top",
            ),
            ])
            ],
            align="top",
        ),

    ],
    fluid=True,
)



def get_country_average(years, months, countries):
    average_changes = [] 
    monthly_averages = pd.DataFrame(columns = ['Country', 'Year', 'Month', 'Reading'])
    averages = [] 
    stations_sum = 0
    for code in countries: 
        stations = stations_europe.loc[stations_europe['CountryCode'] == code]
        temperatures = temperature_monthly.loc[(temperature_monthly['Station'].isin(stations['Station'].to_numpy())) &
        (temperature_monthly['Year'] >= years[0]) & (temperature_monthly['Year'] <= years[1]) & (temperature_monthly['Month'] >= months[0]) & 
        (temperature_monthly['Month'] <= months[1])]
        stations_sum += len(temperatures['Station'].unique())
        yearly_averages = [] 
        for year in range(years[0], years[1] + 1): 
            temps_year = temperatures.loc[temperatures['Year'] == year]
            if(len(temps_year) > 0): 
                temps_sum = 0
                for month in range(months[0], months[1]+1): # each month add up the sum of readings / num of readings 
                    month_temp = temps_year.loc[temps_year['Month'] == month] 
                    if(len(month_temp) > 1): 
                        temps_sum += float(sum(month_temp['Temperature'])/len(month_temp)) #Take avg of common months
                        monthly_averages = monthly_averages.append({'Country': code, 'Year': year, 'Month': month, 'Reading': float(sum(month_temp['Temperature'])/len(month_temp))}, ignore_index=True)
                    elif(len(month_temp) == 1): 
                        temps_sum += float(month_temp['Temperature'])
                        monthly_averages = monthly_averages.append({'Country': code, 'Year': year, 'Month': month, 'Reading': float(month_temp['Temperature'])}, ignore_index=True)
                result = temps_sum / len(temps_year['Month'].unique())
                result = "{:.2f}".format(result)
                yearly_averages.append(float(result)) # average temp of a year 

        if (len(yearly_averages) >= 1):
            averages.append(sum(yearly_averages) / len(yearly_averages))
            average_changes.append(float("{:.2f}".format(float(sum([x - yearly_averages[i - 1] for i, x in enumerate(yearly_averages)][1:]) / len(yearly_averages)))))
        else: 
            averages.append(0)
            average_changes.append(0)
    return average_changes, averages,  monthly_averages, stations_sum


@app.callback(
    dash.dependencies.Output('countryline', 'figure'),
    [dash.dependencies.Input('year-range', 'value'), 
    dash.dependencies.Input('month-range', 'value'),
    dash.dependencies.Input('countrymap', 'selectedData')])
def update_country_line(years, months, countries): 
    fig = go.Figure()
    codes = []
    if countries: 
        for country in countries['points']: 
            codes.append(country['customdata'])
        for code in codes: 
            reading_monthly = temperature_monthly.loc[(code == temperature_monthly['Station']) &
        (temperature_monthly['Year'] >= years[0]) & (temperature_monthly['Year'] <= years[1]) & (temperature_monthly['Month'] >= months[0]) & 
        (temperature_monthly['Month'] <= months[1])]
            reading_monthly['Date'] = pd.to_datetime(reading_monthly[['Year', 'Month']].assign(DAY=1))
            fig.add_trace(go.Scatter(x=reading_monthly['Date'], y=reading_monthly['Temperature'], name=code,
                            mode='lines+markers'))
        fig.update_layout(xaxis_title="Date",yaxis_title="Temperature")
        fig.update_layout(title="Station Readings")
        return fig
    else: 
        fig.update_layout(xaxis_title="Date",yaxis_title="Temperature")
        fig.update_layout(title="Station Readings")
        return fig 





@app.callback(
    dash.dependencies.Output('countrymap', 'figure'),
    dash.dependencies.Input('euromap', 'hoverData'))
def update_country_map(value): 
    if value: 
        return get_country_map(value['points'][0]['customdata'])
    else: 
        return get_country_map('SW')

@app.callback(
    dash.dependencies.Output('euromap', 'figure'),
    dash.dependencies.Output('average-temp', 'children'),
    dash.dependencies.Output('average-temp-change', 'children'),
    dash.dependencies.Output('num-stations', 'children'),[
    dash.dependencies.Input('year-range', 'value'),
    dash.dependencies.Input('month-range', 'value') 
    ])
def update_euro_map(years, months): 
    average_changes, averages, monthly_averages, stations_sum = get_country_average(years, months, country_codes['Code'])

    avg_temp_text = 'Average Temperature: ', float("{:.2f}".format(sum(averages)/len(averages)))
    avg_change_text = 'Average Change: ', float("{:.2f}".format(sum(average_changes)/len(averages)))
    num_stations_text = 'Number of stations: ', stations_sum
    labels = []
    i = 0
    for names in list(country_codes.Name): 
        label = 'Country: ', names, ' Avg. Temp: ', float("{:.2f}".format(averages[i])), ' Avg. Temp Change: ', average_changes[i]
        labels.append(label)
        i+=1

    if abs(max(average_changes)) >= abs(min(average_changes)):
       zmax, zmin = max(average_changes), -max(average_changes)
    else:
       zmax, zmin = abs(min(average_changes)), min(average_changes)


    fig = go.Figure(data=go.Choropleth(locations=list(country_codes.Name),
                locationmode = 'country names',
                colorscale= 'RdBu',
                reversescale=True,
                text= average_changes,
                hoverinfo = 'text', 
                customdata = country_codes.Code, 
                hovertext = labels,
                marker_line_color='Black',
                zmin = zmin, 
                zmax = zmax,
                z=average_changes),

               layout=dict(geo = {'scope':'europe'}))
    fig.update_layout(title="Country View")
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    fig.update_layout(clickmode='event+select')
    return [fig,avg_temp_text, avg_change_text, num_stations_text] 


@app.callback(
    dash.dependencies.Output('euroline', 'figure'),[
    dash.dependencies.Input('year-range', 'value'), 
    dash.dependencies.Input('month-range', 'value'), 
    dash.dependencies.Input('euromap', 'selectedData')
    ])
def update_euro_line(years, months, countries): 
    codes = []
    fig = go.Figure()
    if countries: 
        for country in countries['points']: 
            codes.append(country['customdata'])
        average_changes, averages, monthly_averages, stations_sum = get_country_average(years, months, codes)
        monthly_averages['Date'] = pd.to_datetime(monthly_averages[['Year', 'Month']].assign(DAY=1))
        for code in codes: 
            country_average = monthly_averages.loc[monthly_averages['Country'] == code]
            fig.add_trace(go.Scatter(x=country_average['Date'], y=country_average['Reading'], name=code,
                            mode='lines+markers'))
        fig.update_layout(xaxis_title="Date",yaxis_title="Temperature")
        fig.update_layout(title="Country Readings")
        return fig
    else: 
        fig.update_layout(xaxis_title="Date",yaxis_title="Temperature")
        fig.update_layout(title="Country Readings")
        return fig 
        



@app.callback(
    dash.dependencies.Output('year-start', 'children'),
    dash.dependencies.Output('year-end', 'children'),[
    dash.dependencies.Input('year-range', 'value')])
def update_year_text(years): 
    return years[0], years[1]

@app.callback(
    dash.dependencies.Output('month-start', 'children'),
    dash.dependencies.Output('month-end', 'children'),[
    dash.dependencies.Input('month-range', 'value')])
def update_month_text(months): 
    return months[0], months[1]

        


if __name__ == "__main__":
    app.run_server(debug=False, port=8888)