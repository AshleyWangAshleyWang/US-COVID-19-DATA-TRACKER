import dash
from dash import html
import dash_daq as daq
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.figure_factory as ff
import dash_core_components as dcc
from urllib.request import urlopen
import json

app = dash.Dash(__name__)

# change date format
def create_date_int(data, colname):
    unique_data_sub = pd.DataFrame({
        colname:data[colname].sort_values().unique(),
        'date_number':list(range(data[colname].sort_values().unique().size))
    })
    return pd.merge(data, unique_data_sub, on=colname)

# change state name to full state name
state_name_dict={
    'AK':'Alaska',
    'AL':'Alabama',
    'AR':'Arkansas',
    'AS':'American Samoa',
    'AZ':'Arizona',
    'CA':'California',
    'CO':'Colorado',
    'CT':'Connecticut',
    'DC':'District of Columbia',
    'DE':'Delaware',
    'FL':'Florida',
    'FM':'Federated States of Micronesia',
    'GA':'Georgia',
    'GU':'Guam',
    'HI':'Hawaii',
    'IA':'Iowa',
    'ID':'Idaho',
    'IL':'Illinois',
    'IN':'Indiana',
    'KS':'Kansas',
    'KY':'Kentucky',
    'LA':'Louisiana',
    'MA':'Massachusetts',
    'MD':'Maryland',
    'ME':'Maine',
    'MH':'Marshall Islands',
    'MI':'Michigan',
    'MN':'Minnesota',
    'MO':'Missouri',
    'MP':'Northern Mariana Islands',
    'MS':'Mississippi',
    'MT':'Montana',
    'NC':'North Carolina',
    'ND':'North Dakota',
    'NE':'Nebraska',
    'NH':'New Hampshire',
    'NJ':'New Jersey',
    'NM':'New Mexico',
    'NV':'Nevada',
    'NY':'New York State',
    'OH':'Ohio',
    'OK':'Oklahoma',
    'OR':'Oregon',
    'PA':'Pennsylvania',
    'PR':'Puerto Rico',
    'RI':'Rhode Island',
    'RP':'Republic of Palau',
    'SC':'South Carolina',
    'SD':'South Dakota',
    'TN':'Tennessee',
    'TX':'Texas',
    'UT':'Utah',
    'VA':'Virginia',
    'VI':'Virgin Islands',
    'VT':'Vermont',
    'WA':'Washington',
    'WI':'Wisconsin',
    'WV':'West Virginia',
    'WY':'Wyoming'
}

# data for graph 1
state_ju = pd.read_csv('...COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv')
state_ju.Date=pd.to_datetime(state_ju.Date)
## delete locations that are not state names: BR2, DD2,IH2, VA2
state_ju = state_ju.loc[-state_ju['Location'].isin(['BR2', 'DD2', 'IH2', 'VA2'])]
state_ju = create_date_int(state_ju, 'Date')
state_ju['ful_state_name'] = state_ju['Location'].map(state_name_dict)

# data for graph 2
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
state_county_vacc = pd.read_csv('...COVID-19_Vaccinations_in_the_United_States_County.csv', na_values={'FIPS':'UNK'})
state_county_vacc.Date = pd.to_datetime(state_county_vacc.Date)
state_county_vacc.dropna(subset=['FIPS'], inplace=True)
state_county_vacc = create_date_int(state_county_vacc,'Date')
state_county_vacc['ful_state_name'] = state_county_vacc['Recip_State'].map(state_name_dict)
sub_state_county_vacc = state_county_vacc[['FIPS','Recip_State','Series_Complete_Pop_Pct','Administered_Dose1_Pop_Pct','date_number']]


# data for graph 3 & 4
state_county=pd.read_csv('...United_States_COVID-19_County_Level_of_Community_Transmission_as_Originally_Posted.csv',na_values = ['suppressed'])
state_county.dropna(inplace=True)
state_county.report_date=pd.to_datetime(state_county.report_date)
state_county['new_cases_num'] = state_county.cases_per_100K_7_day_count_change.str.replace(',','').astype('float')
state_county = state_county.loc[state_county['new_cases_num']>0]
state_county = create_date_int(state_county,'report_date')



app.layout = html.Div([
    html.Div([
        html.H1("US COVID-19 DATA TRACKER", style={'font-size':'300%', 'font-family':'verdana'}),
        html.Div([
            html.Div([
                dcc.RadioItems(
                    id='input1_radio_box',
                    options=[{'label': i, 'value': i} for i in ['Fully Vaccinated', 'At least 1 dose']],
                    value='Fully Vaccinated',
                    labelStyle={'display': 'inline-block'}
                )
            ], style={'width': '48%', 'display': 'inline-block'}),  
            
            dcc.Graph(id='graph1_US_state_map-graphic'),

            html.Div(id='onput1_date_result', style={'margin-top': '10px','font-weight':'bold'}),
            html.Div([
                dcc.Slider(
                    id='input2_date_slider',
                    min=0,
                    max=len(state_ju.Date.unique()),
                    value=200,
                ),        
            ], style={'width': '100%'}),
        ]),
    ], style={'text-align': 'center','font-family':'verdana'}),
    

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='input3_state_dropdown',
                options=[{'label': i, 'value': i} for i in state_county_vacc.ful_state_name],
                value='Nevada',
                style={'width': '100%'},
            ),
            dcc.Dropdown(
                id='input4_county_dropdown',
                options=[{'label': i, 'value': i} for i in state_county_vacc.Recip_County],
                value='Nye County',
                style={'width': '100%'},
            )], style={'display': 'flex','width': '50%'}),

        html.Div([
            html.Div([
            dcc.RadioItems(
                id='input5_radio_box',
                options=[{'label': i, 'value': i} for i in ['Fully Vaccinated', 'At least 1 dose']],
                value='Fully Vaccinated',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id='graph2_state_country_map'),
            html.Div(id='check', style={'margin-top': '10px'}),
            html.Div(id='G2onput_date_result', style={'margin-top': '10px','font-weight':'bold'}),
            dcc.Slider(
                id='input6_date_slider', 
                min=0,
                max=len(state_county_vacc.Date.unique()),
                value=300,
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([ # graph 3,4
            html.Div(id='onput2_date_result', style={'margin-top': '10px','font-weight':'bold'}),
            dcc.RangeSlider(
                id='input7_date_range_slider', 
                min=0,
                max=len(state_county.report_date.unique()),
                value=[len(state_county.report_date.unique())//2,(len(state_county.report_date.unique())//2)+10],
                tooltip={"placement": "bottom", "always_visible": False},
                allowCross=False
            ),
            html.H5('Daily % Positivily 7 Daya Moving Avg'),
            
            dcc.Graph(id='graph3_daily_percent_positivily'),
            html.H5('Daily new cases 7 Daya Moving Avg per look'),
            dcc.Graph(id='graph4_daily_new_case'), 
            ], style={'width': '50%', 'display': 'inline-block'}),
        ]),  
    ], style={'text-align': 'center','font-family':'verdana'}),
])

# graph 1
@app.callback(
    Output('graph1_US_state_map-graphic', 'figure'),
    Input('input1_radio_box', 'value'),
    Input('input2_date_slider', 'value'))
def update_graph(input1Radio, input2DateSlider):
    
    sub_date = state_ju.loc[(state_ju.date_number>=0)&(state_ju.date_number <= input2DateSlider)].sort_values(by=['Date'],ascending=False)
    latest_date = sub_date.drop_duplicates(subset=['Location'], keep='first')
    if input1Radio == 'Fully Vaccinated':
        fig = go.Figure(data=go.Choropleth(locations=latest_date['Location'], 
                        z=(latest_date['Series_Complete_Pop_Pct']).astype(float),
                        locationmode='USA-states', 
                        text = latest_date['ful_state_name'],
                        marker_line_color='white',
                        marker_line_width=0.5,
                        colorscale = 'Blues', colorbar_title = "Fully Vaccinated<br>Percent"))
    else:
        fig = go.Figure(data=go.Choropleth(locations=latest_date['Location'], 
                        z=(latest_date['Administered_Dose1_Pop_Pct']).astype(float),
                        locationmode='USA-states', 
                        text = latest_date['ful_state_name'],
                        marker_line_color='white',
                        marker_line_width=0.5,
                        colorscale = 'Blues', colorbar_title = "At Least 1 dose<br>Percent"))

    fig.update_layout(title_text = 'Vaccination Percent of each state in the U.S.',geo_scope='usa',legend_title="Legend Title")
    #, showlegend = True, legend_title='Percent'
    return fig

# graph 2 
@app.callback(
    #Output('check','children'),
    Output('graph2_state_country_map','figure'),
    Input('input6_date_slider', 'value'),
    Input('input3_state_dropdown', 'value'),
    Input('input5_radio_box', 'value'),
    )

def ful_complete_plot(selected_date, selected_state, input5Radio):
    # we need to subset first date & selected date
    sub_place = sub_state_county_vacc.loc[state_county_vacc['ful_state_name']==selected_state]
    sub_date = sub_place.loc[(sub_place.date_number>=0)&(sub_place.date_number <= selected_date)].sort_values(by=['date_number'],ascending=False)
    sub_date = sub_date.drop_duplicates(subset=['FIPS'], keep='first')

    if input5Radio == 'Fully Vaccinated':
        fig = px.choropleth(sub_date, geojson=counties, locations='FIPS', color='Series_Complete_Pop_Pct',
                           color_continuous_scale="Viridis",
                           scope="usa",
                           labels={'Series_Complete_Pop_Pct':'Fully Vaccinated Percent'})
    else:
        fig = px.choropleth(sub_date, geojson=counties, locations='FIPS', color='Administered_Dose1_Pop_Pct',
                           color_continuous_scale="RdBu",
                           scope="usa",
                           labels={'Administered_Dose1_Pop_Pct':'At Least 1 dose Percent'})
    fig.update_layout(title_text = 'Vaccination Percent of each County in the U.S.')
    return fig

# graph 3
@app.callback(
    Output('graph3_daily_percent_positivily','figure'),
    Input('input3_state_dropdown','value'),
    Input('input4_county_dropdown','value'),
    Input('input7_date_range_slider','value')
)
def daily_positive_perccent_graph(sel_state, sel_county, date_range):
    selected_date=state_county.loc[(state_county.date_number>=date_range[0])&(state_county.date_number<=date_range[1])]
    sub_state_county = selected_date.loc[(state_county['state_name']==sel_state)&(state_county['county_name']==sel_county)]
    sub_state_county.sort_values(by='report_date', inplace=True)
    
    fig = px.line(sub_state_county, x="report_date", y="percent_test_results_reported_positive_last_7_days", 
        title='Daily % Positivity - 7 - Day Moving Avg', 
        labels={"report_date": "Date","percent_test_results_reported_positive_last_7_days": "Positive percent rolling average"})
    return fig

# graph 4
@app.callback(
    Output('graph4_daily_new_case','figure'),
    Input('input3_state_dropdown','value'),
    Input('input4_county_dropdown','value'),
    Input('input7_date_range_slider','value')
)
def daily_positive_perccent_graph(sel_state, sel_county, date_range):
    selected_date=state_county.loc[(state_county.date_number>=date_range[0])&(state_county.date_number<=date_range[1])]
    sub_state_county = selected_date.loc[(state_county['state_name']==sel_state)&(state_county['county_name']==sel_county)]
    sub_state_county.sort_values(by='report_date', inplace=True)
    
    fig = px.line(sub_state_county, x="report_date", y="new_cases_num", 
        title='Daily new cases - 7 - Day Moving Avg',
        labels={"report_date": "Date","new_cases_num": "New cases rolling average"})
    return fig

# slider 1 output
@app.callback(
    Output('onput1_date_result', 'children'),
    Input('input2_date_slider', 'value')
)
def update_output(value):
    return 'Selected date till {}'.format(state_ju.loc[state_ju.date_number == value]['Date'].reset_index().Date.astype('str')[0])

# slider 2 output
@app.callback(
    Output('G2onput_date_result', 'children'),
    Input('input6_date_slider', 'value')
)
def update_output(value):
    return 'Selected date till {}'.format(state_county_vacc.loc[state_county_vacc.date_number == value]['Date'].reset_index().Date.astype('str')[0])

# slider 3 output
@app.callback(
    Output('onput2_date_result', 'children'),
    Input('input7_date_range_slider', 'value')
)
def update_output(value):
    return 'Selected date from {} to {}'.format(state_county.loc[state_county.date_number == value[0]]['report_date'].reset_index().report_date.astype('str')[0],
                                                state_county.loc[state_county.date_number == value[1]]['report_date'].reset_index().report_date.astype('str')[0])

# update dropdown options
@app.callback(
    Output('input4_county_dropdown', 'options'),
    Input('input3_state_dropdown', 'value')
)
def update_date_dropdown(input_dropdown_state):
    return [{'label': i, 'value': i} for i in set(state_county_vacc.loc[state_county_vacc['ful_state_name']==input_dropdown_state,'Recip_County'])]


if __name__ == '__main__':
    app.run_server(debug=True)


    