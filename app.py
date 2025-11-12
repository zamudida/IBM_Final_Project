
#Open a new terminal and install the required packages

# python3.13 -m pip install pandas dash
# curl -o spacex_launch_dash.csv "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
# curl -o spacex-dash-app.py "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/t4-Vy4iOU19i8y6E3Px_ww/spacex-dash-app.py"
# python3.13 app.py



# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# --- Prepara las opciones del Dropdown dinámicamente ---
# Primero, obtenemos los nombres únicos de los sitios de lanzamiento
launch_sites = spacex_df['Launch Site'].unique()
# Creamos la lista de opciones, empezando con 'ALL'
options_list = [{'label': 'All Sites', 'value': 'ALL'}]
# Agregamos el resto de los sitios
for site in launch_sites:
    options_list.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# --- Create an app layout ---
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=options_list,  # Usamos la lista de opciones que creamos
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,  # Usamos el min_payload calculado
        max=max_payload,  # Usamos el max_payload calculado
        step=1000,
        # Creamos marcas para el slider
        marks={i: f'{i} Kg' for i in range(int(min_payload), int(max_payload) + 1, 2500)},
        value=[min_payload, max_payload]  # Valor inicial es el rango completo
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# --- FIN DEL LAYOUT ---

# --- CALLBACKS ---

# TASK 2: Callback para el Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Si 'ALL', agrupamos por 'Launch Site' y sumamos los éxitos ('class' = 1)
        fig_data = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='success_count')
        fig = px.pie(
            fig_data, 
            values='success_count', 
            names='Launch Site', 
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Si es un sitio específico, filtramos por ese sitio
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Contamos los éxitos (1) y fracasos (0)
        site_data = filtered_df['class'].value_counts().reset_index(name='count')
        # Mapeamos 0/1 a Fail/Success para mejor legibilidad
        site_data['class'] = site_data['class'].map({1: 'Success', 0: 'Failed'})
        
        fig = px.pie(
            site_data,
            values='count',
            names='class',
            title=f'Total Success vs. Failed Launches for {entered_site}',
            color='class', # Colorea basado en Éxito/Fallo
            color_discrete_map={'Success':'green', 'Failed':'red'} # Asigna colores
        )
        return fig

# TASK 4: Callback para el Scatter Chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    # 1. Filtramos por el rango del payload seleccionado en el slider
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # 2. Filtramos por el sitio, si no es 'ALL'
    if entered_site == 'ALL':
        # Graficamos todos los sitios
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',  # 0 para fallo, 1 para éxito
            color='Booster Version Category',  # Coloreamos por versión del booster
            title='Payload vs. Launch Outcome for All Sites'
        )
        return fig
    else:
        # Graficamos solo el sitio seleccionado
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Launch Outcome for {entered_site}'
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run()