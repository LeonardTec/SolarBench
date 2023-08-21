import pandas as pd
import pandasql
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


#Step 1: Import Data File and Process Data


data = pd.read_csv("table.csv")
name = "Energy Consumption over Time"
time = data["Time"].to_list()
timesFilled = data["Current"].to_list()

#Step 2: Dash webapp design using CSS and dash app initialization
external_stylesheets = ['cssSheet.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Table Energy Usage Data'


figure = go.Figure(data=[
        go.Bar(name='michelleBarnett', x=time, y=timesFilled,marker_color='#FCEEA5')
    ])
figure.update_layout(barmode='group')
figure.layout = {
    'title': dict(
        text=name,
        x = 0.5,
        font=dict(
            family='Courier New, monospace',
            size=24,
            color='#FCEEA5'
        )
    ),
    'xaxis' : dict(
        title='Time',
        titlefont=dict(
            family='Courier New, monospace',
            size=24,
            color='#FCEEA5'
        )
    ),
    'yaxis' : dict(
        title='Current Used (A)',
        titlefont=dict(
            family='Courier New, monospace',
            size=24,
            color='#FCEEA5'
        )
    )
}
figure.layout.plot_bgcolor = '#101010'
figure.layout.paper_bgcolor =  '#101010'
figure.update_xaxes(tickangle=0, tickfont=dict(family='Courier New, monospace', color='#FCEEA5', size=14))
figure.update_yaxes(tickangle=0, tickfont=dict(family='Courier New, monospace', color='#FCEEA5', size=14))
figure.update_layout(xaxis=dict(showgrid=False, zeroline=False),yaxis=dict(showgrid=False, zeroline=False),)
figure.update_traces(marker_line_width=0)
figure.update_layout(
    legend=dict(
        font=dict(
            family='Courier New, monospace',
            size=16,
            color='#FCEEA5'
        ),
        bgcolor='#101010',
        bordercolor='#FCEEA5',
        borderwidth=2
    )
)
figure.update_layout(hovermode='x')

app.layout = html.Div(children=[

    dcc.Graph(
        id='example-graph',
        figure=figure
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)