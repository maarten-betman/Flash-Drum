import dash
import dash_core_components as dcc
import dash_html_components as html


app = dash.Dash()

app.layout = html.Div([
    html.Label('Mixture: '),
    dcc.Dropdown(
        id = 'components',
        options=[
            {'label': 'Benzene', 'value': 'BENZENE'},
            {'label': 'Toluene', 'value': 'TOLUENE'}
        ],
        placeholder = 'Select two or more',
        multi = True
    )
])

if __name__ == "__main__":
    app.run_server(port = 80, debug = True)