# pv_app.py
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__)
app.title = "Solar Performance Dashboard"

font_style = {
    'font-family': 'Arial, sans-serif',
    'color': '#333333'
}

header_style = {
    'backgroundColor': '#d4e0e3',
    'color': '002b84',
    'padding': '10px',
    'textAlign': 'center'
}

label_style = {
    'font-size': '18px',
    'margin': '10px 0'
}

input_style = {
    'font-size': '16px',
    'width': '100%',
    'padding': '10px',
    'border': '1px solid #ccc',
    'border-radius': '5px'
}

button_style = {
    'font-size': '16px',
    'backgroundColor': '#002b84',
    'color': 'white',
    'padding': '10px 20px',
    'border': 'none',
    'border-radius': '5px',
    'cursor': 'pointer',
    'margin-top': '10px'
}

card_style = {
    'padding': '20px',
    'border': '1px solid #afbec2',
    'border-radius': '5px',
    'text-align': 'center',
    'backgroundColor': '#f9f9f9',
    'margin': '10px'
}

container_style = {
    'display': 'flex',
    'flexWrap': 'wrap',
    'justifyContent': 'space-between',
    'padding': '10px'
}

graph_container_style = {
    'flex': '1',
    'padding': '10px',
    'backgroundColor': '#ffffff',
    'border': '1px solid #afbec2',
    'border-radius': '5px',
    'margin': '10px'
}

app.layout = html.Div(style=font_style, children=[
    html.Div([
        html.H1("Solar Performance Dashboard", style={'font-size': '32px', 'font-weight': 'bold'}),
    ], style=header_style),
    html.Div([
        html.Div([
            html.Label("Latitude:", style=label_style),
            dcc.Input(id='latitude', type='number', value=56.01226316057495, step=0.01, style=input_style),
        ], style={'flex': '1', 'padding': '10px'}),
        html.Div([
            html.Label("Longitude:", style=label_style),
            dcc.Input(id='longitude', type='number', value=-3.779039941114147, step=0.01, style=input_style),
        ], style={'flex': '1', 'padding': '10px'}),
        html.Div([
            html.Label("Peak Power (kW):", style=label_style),
            dcc.Input(id='peakpower', type='number', value=250, step=0.1, style=input_style),
        ], style={'flex': '1', 'padding': '10px'}),
    ], style=container_style),
    html.Button(id='submit-button', n_clicks=0, children='Submit', style=button_style),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=[
            html.Div(id='high-level-numbers', style={'display': 'flex', 'justify-content': 'space-around', 'margin': '20px 0'}),
            html.Div([
                html.Div(dcc.Graph(id='hourly-irradiance'), style=graph_container_style),
                html.Div(dcc.Graph(id='monthly-avg-irradiance'), style=graph_container_style),
            ], style={'display': 'flex', 'justify-content': 'space-between'}),
            html.Div(dcc.Graph(id='monthly-generation-roof-pitch'), style=graph_container_style),
            html.Div([
                html.Div(dcc.Graph(id='financial-performance'), style=graph_container_style),
                html.Div([
                    html.Div(id='monthly-return', style=card_style),
                    html.Div(id='yearly-return', style=card_style),
                    html.Div(id='co2-saved', style=card_style)
                ], style={'flex': '1', 'padding': '10px'})
            ], style={'display': 'flex'})
        ]
    )
])

@app.callback(
    [Output('high-level-numbers', 'children'),
     Output('hourly-irradiance', 'figure'),
     Output('monthly-avg-irradiance', 'figure'),
     Output('monthly-generation-roof-pitch', 'figure'),
     Output('financial-performance', 'figure'),
     Output('monthly-return', 'children'),
     Output('yearly-return', 'children'),
     Output('co2-saved', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('latitude', 'value'),
     State('longitude', 'value'),
     State('peakpower', 'value')]
)
def update_graphs(n_clicks, lat, lon, peakpower):
    base_url_hourly = "https://re.jrc.ec.europa.eu/api/seriescalc?"
    params_hourly = {
        "lat": lat,
        "lon": lon,
        "peakpower": peakpower,
        "loss": 5,
        "pvtechchoice": "crystSi",
        "angle": 15,
        "aspect": 0,
        "outputformat": "json",
        "browser": 0
    }
    response_hourly = requests.get(base_url_hourly, params=params_hourly)
    if response_hourly.status_code == 200:
        data_hourly = response_hourly.json()
    else:
        return {}, {}, {}, {}, {}, {}, {}, {}

    hourly_data = data_hourly['outputs']['hourly']
    df_hourly = pd.DataFrame(hourly_data)
    df_hourly['time'] = pd.to_datetime(df_hourly['time'], format='%Y%m%d:%H%M')
    df_hourly['month'] = df_hourly['time'].dt.month
    df_hourly['hour'] = df_hourly['time'].dt.hour

    hourly_avg = df_hourly.groupby('hour')['G(i)'].mean().reset_index()
    fig_hourly_irradiance = px.line(hourly_avg, x='hour', y='G(i)', title='Hourly Irradiance Throughout the Year')
    fig_hourly_irradiance.update_layout(xaxis_title='Hour of the Day', yaxis_title='Global Irradiance (W/m²)')

    monthly_hourly_avg = df_hourly.pivot_table(values='G(i)', index='hour', columns='month', aggfunc='mean')
    fig_monthly_avg_irradiance = go.Figure(data=go.Heatmap(
        z=monthly_hourly_avg.values,
        x=monthly_hourly_avg.columns,
        y=monthly_hourly_avg.index,
        colorscale='Viridis'
    ))
    fig_monthly_avg_irradiance.update_layout(title='Monthly Average Hourly Irradiance', xaxis_title='Month', yaxis_title='Hour of the Day')

    base_url_angle = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?"
    params_angle = {
        "lat": lat,
        "lon": lon,
        "peakpower": peakpower,
        "loss": 5,
        "aspect": 0,
        "pvtechchoice": "crystSi",
        "outputformat": "json",
        "browser": 0
    }
    angle_data = []
    for angle in range(0, 90, 10):
        params_angle['angle'] = angle
        response_angle = requests.get(base_url_angle, params=params_angle)
        if response_angle.status_code == 200:
            data_angle = response_angle.json()
            monthly_data = data_angle['outputs']['monthly']['fixed']
            for record in monthly_data:
                record['angle'] = angle
            angle_data.extend(monthly_data)
        else:
            print(f"Error: {response_angle.status_code} - {response_angle.text}")
    df_angle = pd.DataFrame(angle_data)

    fig_monthly_generation_roof_pitch = px.line(df_angle, x='month', y='E_m', color='angle', title='Monthly Generation by Roof Pitch')
    fig_monthly_generation_roof_pitch.update_layout(xaxis_title='Month', yaxis_title='Total Monthly Energy Production (kWh)')

    energy_price_per_kWh = 0.06  # Energy price in £ per kWh
    df_angle['monthly_revenue'] = df_angle['E_m'] * energy_price_per_kWh
    fig_financial_performance = px.line(df_angle, x='month', y='monthly_revenue', color='angle', title='Monthly Revenue from Energy Sold to Grid')
    fig_financial_performance.update_layout(xaxis_title='Month', yaxis_title='Revenue (£)')

    response_high_level = requests.get(base_url_angle, params=params_angle)
    if response_high_level.status_code == 200:
        data_high_level = response_high_level.json()
        E_d = data_high_level['outputs']['totals']['fixed']['E_d']
        E_m = data_high_level['outputs']['totals']['fixed']['E_m']
        H_i_d = data_high_level['outputs']['totals']['fixed']['H(i)_d']
    else:
        E_d, E_m, H_i_d = None, None, None

    high_level_numbers = [
        html.Div([
            html.H3(f"{E_d:.2f}" if E_d else "N/A"),
            html.P("Average Daily Energy Production (kWh/d)")
        ], style=card_style),
        html.Div([
            html.H3(f"{E_m:.2f}" if E_m else "N/A"),
            html.P("Average Monthly Energy Production (kWh/mo)")
        ], style=card_style),
        html.Div([
            html.H3(f"{H_i_d:.2f}" if H_i_d else "N/A"),
            html.P("Average Daily Sum of Global Irradiation (kWh/m²/d)")
        ], style=card_style)
    ]

    monthly_revenue = df_angle['monthly_revenue'].sum() / 12 if not df_angle.empty else 0
    yearly_revenue = df_angle['monthly_revenue'].sum() if not df_angle.empty else 0

    monthly_return_text = [
        html.H3(f"£{monthly_revenue:.2f}"),
        html.P("Average Monthly Return")
    ]

    yearly_return_text = [
        html.H3(f"£{yearly_revenue:.2f}"),
        html.P("Total Yearly Return")
    ]

    CO2_per_kWh = 0.3900894  # kg CO2 per kWh
    yearly_co2_saved = yearly_revenue / energy_price_per_kWh * CO2_per_kWh if yearly_revenue else 0

    co2_saved_text = [
        html.H3(f"{yearly_co2_saved:.2f} kg"),
        html.P("Total CO2 Saved per Year")
    ]

    return high_level_numbers, fig_hourly_irradiance, fig_monthly_avg_irradiance, fig_monthly_generation_roof_pitch, fig_financial_performance, monthly_return_text, yearly_return_text, co2_saved_text

if __name__ == '__main__':
    app.run_server(debug=True)
