import os
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import io
import base64
from dash.exceptions import PreventUpdate

# Inicialización de la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Estilos personalizados
styles = {
    'upload-box': {
        'width': '100%',
        'height': '70px',
        'lineHeight': '70px',
        'borderWidth': '2px',
        'borderStyle': 'dashed',
        'borderRadius': '15px',
        'textAlign': 'center',
        'margin': '20px 0',
        'backgroundColor': '#f4f4f9',
        'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.1)',
        'transition': 'all 0.3s ease-in-out',
    },
    'button': {
        'backgroundColor': '#4CAF50',
        'color': 'white',
        'border': 'none',
        'padding': '12px 24px',
        'borderRadius': '50px',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease-in-out',
        'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.2)',
    },
}

# Función para procesar el archivo CSV
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        # Leer archivo CSV
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Crear figura 3D
        fig = go.Figure()
        
        # Graficar Pozos
        for pozo in df['pozo'].unique():
            df_pozo = df[df['pozo'] == pozo]
            fig.add_trace(go.Scatter3d(
                x=df_pozo['x'],
                y=df_pozo['y'],
                z=df_pozo['z'],
                mode='lines+markers',
                name=f'Pozo {pozo}',
                line=dict(width=6),
                marker=dict(size=8)
            ))
        
        # Graficar litologias
        for litologia in df['litologia'].unique():
            df_litologia = df[df['litologia'] == litologia]
            x = df_litologia['x'].values
            y = df_litologia['y'].values
            z = df_litologia['z'].values
            
            fig.add_trace(go.Mesh3d(
                x=x,
                y=y,
                z=z,
                opacity=0.5,
                name=f'litologia {litologia}',  # Mostrar nombre en la leyenda
                showlegend=True
            ))
        
        # Actualizar layout
        fig.update_layout(
            scene=dict(
                zaxis=dict(
                    autorange=True,
                    title='Profundidad'
                )
            ),
            title=f"Trayectorias y litologias 3D - {filename}",
            plot_bgcolor='#f9f9f9',  # Fondo claro en el gráfico
        )
        
        return fig
    
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        return go.Figure()

# Layout de la aplicación
app.layout = dbc.Container([
    dbc.Tabs([
        dbc.Tab([
            dbc.Row([ 
                dbc.Col([                    
                    # Instrucciones con ejemplo de archivo CSV
                    html.Hr(),
                    html.P("Esta aplicación diseñada con Dash de Python, permite crear gráficas interactivas en 3D para visualizar las trayectorias de perforación, "
                           "así como las litologias que estas atraviesan. Para generar una gráfica, se requiere cargar un archivo CSV con la información de cada punto, "
                           "organizada de la siguiente manera:"),
                    
                    # Tabla de ejemplo de datos
                    dbc.Table([
                        html.Thead(html.Tr([html.Th("pozo"), html.Th("litologia"), html.Th("x"), html.Th("y"), html.Th("z")])),
                        html.Tbody([
                            html.Tr([html.Td("pozo_1"), html.Td("litologia_1"), html.Td("264472.7833"), html.Td("1099592.361"), html.Td("0")]),
                            html.Tr([html.Td("pozo_2"), html.Td("litologia_2"), html.Td("264472.7833"), html.Td("1099592.361"), html.Td("-2528")]),
                            html.Tr([html.Td("pozo_3"), html.Td("litologia_3"), html.Td("264473.95"), html.Td("1099593.317"), html.Td("-2812")]),
                            html.Tr([html.Td("pozo_4"), html.Td("litologia_4"), html.Td("264458.6556"), html.Td("1099600.539"), html.Td("-3223")]),
                            html.Tr([html.Td("pozo_5"), html.Td("litologia_5"), html.Td("264109.8611"), html.Td("1099706.583"), html.Td("-4603")])
                        ])
                    ], bordered=True, hover=True, responsive=True),
                ], width=12)
            ], style={'backgroundColor': '#fafafa'})
        ], label="Introducción", tab_id="tab-intro"),
        
        dbc.Tab([
            dbc.Row([ 
                dbc.Col([ 
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div(['Arrastra o selecciona el archivo CSV']),
                        style=styles['upload-box']
                    ),
                ], md=6),
            ]),
            
            dbc.Row([ 
                dbc.Col([ 
                    dcc.Graph(id='3d-visualization', style={'height': '80vh'})
                ])
            ]),

            dbc.Row([ 
                dbc.Col([ 
                    html.Button("Mostrar en Pantalla Completa", id="fullscreen-button", style=styles['button'])
                ], className="text-center")
            ])
        ], label="Visualización 3D", tab_id="tab-viz")
    ], style={'backgroundColor': '#f5f5f5'})
], fluid=True)

# Callback para actualizar la visualización con el archivo cargado
@app.callback(
    Output('3d-visualization', 'figure'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_graph(contents, filename):
    if contents is not None:
        return parse_contents(contents, filename)
    return go.Figure()

# Callback de pantalla completa
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            var elem = document.getElementById('3d-visualization');
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) {
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                elem.msRequestFullscreen();
            }
        }
        return '';
    }
    """,
    Output('fullscreen-button', 'children'),
    Input('fullscreen-button', 'n_clicks'),
    prevent_initial_call=True
)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))

server = app.server
