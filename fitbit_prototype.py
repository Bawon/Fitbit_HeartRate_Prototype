import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import os


app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
user_session = {'username': None}


login_layout = html.Div([
    dcc.Input(id='username', type='text', placeholder='Enter your name'),
    html.Button('Login', id='login-button', n_clicks=0),
])


def after_login_layout():
    return html.Div([
        html.Button('Die Young Kesha', id='btn-dieyoung', n_clicks=0),
        html.Button('Chopin Opus 9 No 2', id='btn-chopin', n_clicks=0),
        html.Button('Bangerang Skrillex', id='btn-bangerang', n_clicks=0),
        html.Button('Slipknot psychosocial', id='btn-slipknot', n_clicks=0),
        html.Div(id='container-button-timestamp')
    ])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=login_layout)
])

@app.callback(Output('page-content', 'children'),
              [Input('login-button', 'n_clicks')],
              [State('username', 'value')],
              prevent_initial_call=True)
def display_page(n_clicks, username):
    if n_clicks > 0 and username:
        user_session['username'] = username
        return after_login_layout()
    else:
        return login_layout

def analyze_mood(heart_rate):
    #Pretty bad mood analysis
    if heart_rate > 81:
        return "Stressed"
    elif heart_rate < 74:
        return "Relaxed"
    else:
        return "Normal"


@app.callback(
    Output('container-button-timestamp', 'children'),
    [Input('btn-dieyoung', 'n_clicks'),
     Input('btn-chopin', 'n_clicks'),
     Input('btn-bangerang', 'n_clicks'),
     Input('btn-slipknot', 'n_clicks')],
    prevent_initial_call=True)
def display_graph(btn1, btn2, btn3, btn4):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    song_map = {
        'btn-dieyoung': 'Die_Young_Kesha',
        'btn-chopin': 'Chopin_Opus_9_No_2',
        'btn-bangerang': 'Bangerang_Skrillex',
        'btn-slipknot': 'Slipknot_psychosocial'
    }

    song_name = song_map.get(button_id)
    if song_name:
        username = user_session['username']
        data_folder = 'data'
        file_path = os.path.join(data_folder, username, f"{song_name}.csv")
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['time'] = pd.to_datetime(df['time'])
            start_time = df['time'].iloc[0]
            df['elapsed_time'] = df['time'].apply(lambda x: (x - start_time).total_seconds())

            avg_heart_rate = df['value'].mean()
            mood = analyze_mood(avg_heart_rate)

            fig = px.line(df, y='value', x='elapsed_time', labels={'elapsed_time': 'Time Elapsed (seconds)', 'value': 'Heart Rate'})
            graph = dcc.Graph(figure=fig)

            return html.Div([graph, html.P(f"Average Heart Rate: {avg_heart_rate:.2f} bpm - Mood: {mood}")])
        
        else:
            return html.Div("Data file not found: " + file_path)
    return html.Div("No song selected")

if __name__ == '__main__':
    app.run_server(debug=True)