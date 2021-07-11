import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

class Controls: 

    def get_controls(): 
        return dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Year Range"),
                dcc.RangeSlider(
                    id = 'year-range',
                    min=1949,
                    max=2017,
                    step=1,
                    marks={
                        1949: '1949',  
                        1960: '1960', 
                        1970: '1970',
                        1980: '1980', 
                        1990: '1990', 
                        2000: '2000', 
                        2010: '2010', 
                        2017: '2017'
                    },
                    value=[1949, 2017]
                )
            ]
        ),
       
        dbc.Row([html.P(id="year-start",  style={'width': 50, 'margin-right': '195px', 'margin-bottom': '20px', 'margin-left':'30px'}),
        html.P(id="year-end", style={'width': 50, 'margin-left': '40px'})]),
        
        dbc.FormGroup(
            [
                dbc.Label("Month Range"),
                dcc.RangeSlider(
                    id = 'month-range',
                    min=1,
                    max=12,
                    step=None,
                    marks={
                        1: 'Jan',
                        2: 'Feb',
                        3: 'Mar',
                        4: 'Apr',
                        5: 'May', 
                        6: 'Jun', 
                        7: 'Jul', 
                        8: 'Aug', 
                        9: 'Sep', 
                        10: 'Oct', 
                        11: 'Nov', 
                        12: 'Dec'
                    },
                    value=[1, 12]
                )
            ]
            
        ), 
        dbc.Row([html.P(id="month-start",  style={'width': 50, 'margin-right': '195px', 'margin-bottom': '20px', 'margin-left':'30px'}),
        html.P(id="month-end", style={'width': 50, 'margin-left': '50px'})]), 

        dbc.Card([html.P('Average Temperature: ' ,id='average-temp'),
        html.P('Average Change: ' ,id='average-temp-change'),
        html.P('Number of stations: ' ,id='num-stations') ])
    ],
    body=True,

)

    