import numpy as np
import requests
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import json
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from io import BytesIO
import base64


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
],)
server = app.server

dados_estados = pd.read_csv("./date/especies_ameacadas_por_estados.csv")
dadosbiomas = pd.read_csv("./date/especies_ameacadas_por_biomas.csv")
geojson_estados = json.load(open('./assets/Brasil.json'))
geojson_biomas = json.load(open('./assets/biomas_brasil.json'))
dados_estados.reset_index(inplace=True)
dadosbiomas.reset_index(inplace=True)

# ----------------------------------------------
dados = pd.read_csv('./date/dados_tratados.csv')
dados.head()

dados.drop('Unnamed: 0', axis=1, inplace=True)

dados.head()

dados['Estados de Ocorrência'].str.contains('^F.*')

lista_ameacas = []
ameacas = ''

for i in dados.get('Principais Ameaças'):
    ameacas = i.split(',')
    for ameaca in ameacas:
        if ameaca not in lista_ameacas and ameaca != '':
            lista_ameacas.append(ameaca)

# print(lista_ameacas)

lista_biomas = []
biomas = ''

for i in dados.get('Bioma'):
    biomas = i.split(',')
    for bioma in biomas:
        if bioma not in lista_biomas and bioma != '':
            lista_biomas.append(bioma)

# print(lista_biomas)

dados['Estados de Ocorrência'] = dados['Estados de Ocorrência'].astype(str)

lista = []
ufs = ''

for i in dados.get('Estados de Ocorrência'):
    ufs = i.split(',')
    for uf in ufs:
        if uf not in lista and uf != '':
            lista.append(uf)

# print(lista)
# print(len(lista))


def generate_bar_chart(df, column, filter_columns, title, xaxis=dict(), yaxis=dict(), legend={'x': 1, 'y': 1}, orientation='h', barmode='stack'):
    fig = go.Figure()
    for key, values_list in filter_columns.items():
        for item in values_list:
            df_filtered = df[df[key] == item]
            axis = df_filtered[column].value_counts()
            fig.add_trace(
                go.Bar(
                    x=axis.values if orientation == 'h' else axis.index,
                    y=axis.index if orientation == 'h' else axis.values,
                    name=item,
                    orientation=orientation
                )
            )

    fig.update_layout(barmode=barmode, xaxis=xaxis, yaxis=yaxis, legend={
                      **legend, 'bgcolor': 'rgba(255, 255, 255, 0)', 'bordercolor': 'rgba(255, 255, 255, 0)'}, template="plotly_dark")
    return fig


# cloud_mask = np.array(Image.open(requests.get('https://lh3.googleusercontent.com/proxy/xxQLBFLx2RC-OQ7gn-D7UUACbTUnJQlJCMRyeU4nDGYZXafHeXMPpZx5IF021TT51ajfwUoQf8ZM5f_3cVIVayOL8qHXNWUVl1QmfFK1tdM1BSQpXKDgwVogeTT0ZWY2o8BQzvs4xstzhQ4ggw', stream=True).raw))

def plot_wordcloud(data, shape):
    d = {a: x for a, x in data.values}
    wc = WordCloud(width=500, height=500, scale=1.0)
    wc.fit_words(d)
    return wc.to_image()


def add(a, b, c, d, e):
    return a + b + c + d + e


categoria = {
    'VU': 1,
    'EN': 2,
    'CR': 3
}


nivel_protecao = {
    0: 5,
    1: 4,
    2: 3,
    3: 2,
    4: 1,
    5: 0
}

protecao = {
    'Sim': 0,
    'Não': 1
}


exclusiva = {
    'Sim': 1,
    'Não': 0,
    'Informação não disponível': 0
}

dados = pd.read_csv('./date/dados_tratados.csv')
dados_separados = pd.read_csv('./date/dados_separados.csv')
dados_biomas = pd.read_csv('./date/dados_biomas.csv')

dados_ameacas = dados
dados_ameacas.rename(
    columns={"Principais Ameaças": "Principais_ameacas"}, inplace=True)
dados_ameacas = dados_ameacas.assign(
    Principais_ameacas=dados['Principais_ameacas'].str.split(",")).explode('Principais_ameacas')

dados_ameacas_qtd = dados.set_index(dados['Espécie (Simplificado)'])
dados_ameacas_qtd['qtd_ameacas'] = dados_ameacas['Espécie (Simplificado)'].value_counts(
)
dados_ameacas_qtd['total_ameacas'] = dados_ameacas_qtd.apply(
    lambda row: add(
        row['qtd_ameacas'],
        # categoria[row['Sigla Categoria de Ameaça']],
        nivel_protecao[row['Nível de Proteção na Estratégia Nacional']],
        protecao[row['Presença em Áreas Protegidas']
                 if row['Presença em Áreas Protegidas'] in ['Sim', 'Não'] else 'Sim'],
        protecao[row['Plano de Ação Nacional para Conservação (PAN)']],
        exclusiva[row['Espécie exclusiva do Brasil']]
    ), axis=1
)
ameacas_fauna = dados_ameacas_qtd[dados_ameacas_qtd['Fauna/Flora'] == 'Fauna']
ameacas_flora = dados_ameacas_qtd[dados_ameacas_qtd['Fauna/Flora'] == 'Flora']
fig1 = go.Figure(data=[go.Pie(labels=dados['Espécie exclusiva do Brasil'].unique(
), values=dados['Espécie exclusiva do Brasil'].value_counts(), hole=.3,)])
fig1.update_layout(template="plotly_dark")

fig2 = generate_bar_chart(
    dados,
    "Grupo",
    {"Espécie exclusiva do Brasil": [
        "Sim", "Não", "Informação não disponível"]},
    "Perfil dos Grupos em relação a exclusividade no Brasil",
    xaxis={'title': 'Quantidade de espécies'},
    yaxis={'title': 'Grupos'},
    legend={'x': 0.7, 'y': 1},
)
fig3 = generate_bar_chart(
    dados_biomas,
    "Bioma",
    {"Espécie exclusiva do Brasil": [
        "Sim", "Não", "Informação não disponível"]},
    "Perfil dos Biomas em relação a exclusividade no Brasil",
    xaxis={'title': 'Quantidade de espécies'},
    yaxis={'title': 'Biomas'},
    legend={'x': 0.7, 'y': 1}
)

fig4 = go.Figure(data=[go.Pie(labels=dados_biomas.loc[dados_biomas['Espécie exclusiva do Brasil'] == 'Sim', 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index().index,
                              values=dados_biomas.loc[dados_biomas['Espécie exclusiva do Brasil'] == 'Sim', 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index(), hole=.4)])
fig4.update_layout(colorway=[
                   '#EF553B', '#636EFA'], template="plotly_dark")


fig5 = go.Figure(data=[go.Pie(labels=dados_biomas.loc[dados_biomas['Espécie exclusiva do Brasil'] == 'Não', 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index().index,
                              values=dados_biomas.loc[dados_biomas['Espécie exclusiva do Brasil'] == 'Não', 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index(), hole=.4)])
fig5.update_layout(colorway=[
                   '#636EFA', '#EF553B'], legend_traceorder='reversed', template="plotly_dark")

fig6 = generate_bar_chart(
    dados,
    "Grupo",
    {"Plano de Ação Nacional para Conservação (PAN)": ["Sim", "Não"]},
    "Perfil dos Grupos em relação a presença de um Plano de Ação Nacional Para Conservação",
    xaxis={'title': 'Quantidade de espécies'},
    yaxis={'title': 'Grupo'},
    legend={'x': 0.7, 'y': 1},
)

fig7 = generate_bar_chart(
    dados_biomas,
    "Bioma",
    {"Plano de Ação Nacional para Conservação (PAN)": ["Sim", "Não"]},
    "Perfil dos Biomas em relação a presença de um Plano de Ação Nacional Para Conservação",
    xaxis={'title': 'Quantidade de espécies'},
    yaxis={'title': 'Bioma'},
    legend={'x': 0.7, 'y': 1},
)

# ----------------------------------------------

map_graph = html.Div([
    html.Br(),
    html.H5("Espécies ameaçadas por Estados",
            style={'text-align': 'center'}),

    dcc.Dropdown(id="estados_select",
                 options=[
                     {"label": "Quantidade total de espécies ameaçadas",
                      "value": "Espécies ameaçadas"},
                     {"label": "Fauna", "value": "Fauna espécies ameaçadas"},
                     {"label": "Flora", "value": "Flora espécies ameaçadas"},
                     {"label": "Angiospermas",
                      "value": "Angiospermas espécies ameaçadas"},
                     {"label": "Anfíbios", "value": "Anfíbios espécies ameaçadas"},
                     {"label": "Aves", "value": "Aves espécies ameaçadas"},
                     {"label": "Briófitas",
                      "value": "Briófitas espécies ameaçadas"},
                     {"label": "Gimnospermas",
                      "value": "Gimnospermas espécies ameaçadas"},
                     {"label": "Invertebrados aquaticos",
                      "value": "Invertebrados aquaticos espécies ameaçadas"},
                     {"label": "Invertebrados terrestres",
                      "value": "Invertebrados terrestres espécies ameaçadas"},
                     {"label": "Mamiferos",
                      "value": "Mamiferos espécies ameaçadas"},
                     {"label": "Peixes continentais",
                      "value": "Peixes continentais espécies ameaçadas"},
                     {"label": "Peixes marinhos",
                      "value": "Peixes marinhos espécies ameaçadas"},
                     {"label": "Pteridofitas",
                      "value": "Pteridofitas espécies ameaçadas"},
                     {"label": "Repteis", "value": "Repteis espécies ameaçadas"}],
                 multi=False,
                 clearable=False,
                 value="Espécies ameaçadas",
                 ),
    dcc.Graph(id='my_bee_map', figure={}),
])


@app.callback(
    Output(component_id='my_bee_map', component_property='figure'),
    [Input(component_id='estados_select', component_property='value')]
)
def update_graph(option_slctd):
    dff = dados_estados.copy()

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        geojson=geojson_estados,
        locations='Estado_de_Ocorrencia',
        scope="south america",
        color=option_slctd,
        hover_data=['Estado_de_Ocorrencia'],
        template='plotly_dark',
    )
    return fig


map_biomas = html.Div([
    html.Br(),
    html.H5("Espécies ameaçadas por Biomas",
            style={'text-align': 'center'}),
    dcc.Dropdown(id="biomas_select",
                 options=[
                     {"label": "Quantidade total de espécies ameaçadas",
                      "value": "Espécies ameaçadas"},
                     {"label": "Angiospermas",
                      "value": "Angiospermas espécies ameaçadas"},
                     {"label": "Anfíbios", "value": "Anfíbios espécies ameaçadas"},
                     {"label": "Aves", "value": "Aves espécies ameaçadas"},
                     {"label": "Briófitas",
                      "value": "Briófitas espécies ameaçadas"},
                     {"label": "Gimnospermas",
                      "value": "Gimnospermas espécies ameaçadas"},
                     {"label": "Invertebrados aquaticos",
                      "value": "Invertebrados aquaticos espécies ameaçadas"},
                     {"label": "Invertebrados terrestres",
                      "value": "Invertebrados terrestres espécies ameaçadas"},
                     {"label": "Mamiferos",
                      "value": "Mamiferos espécies ameaçadas"},
                     {"label": "Peixes continentais",
                      "value": "Peixes continentais espécies ameaçadas"},
                     {"label": "Peixes marinhos",
                      "value": "Peixes marinhos espécies ameaçadas"},
                     {"label": "Pteridofitas",
                      "value": "Pteridofitas espécies ameaçadas"},
                     {"label": "Repteis", "value": "Repteis espécies ameaçadas"}],
                 multi=False,
                 clearable=False,
                 value="Espécies ameaçadas",
                 ),

    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='my_bee_map2', figure={})),
            dbc.Col(dcc.Graph(id='my_bee_map3', figure={})),
        ]
    ),

])
# Connect the Plotly graphs with Dash Components


@ app.callback(
    [Output(component_id='my_bee_map2', component_property='figure'),
     Output(component_id='my_bee_map3', component_property='figure')],
    [Input(component_id='biomas_select', component_property='value')]
)
def update_graph(option_slctd):
    container = "The year chosen by user was: {}".format(option_slctd)

    dff = dadosbiomas.copy()

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        geojson=geojson_biomas,
        locations='Bioma',
        scope="south america",
        color=option_slctd,
        hover_data=['Bioma'],
        template='plotly_dark',
    )

    fig_bar_dados_biomas = px.bar(dff, y=option_slctd, x='Bioma', template='plotly_dark',
                                  text=option_slctd, color=option_slctd, color_continuous_scale='Reds')
    fig_bar_dados_biomas.update_traces(
        texttemplate='%{text:.2s %}', textposition='outside')
    fig_bar_dados_biomas.update_layout(
        uniformtext_minsize=8, uniformtext_mode='hide')
    fig_bar_dados_biomas.update_layout(
        xaxis={'categoryorder': 'total ascending'})

    return fig, fig_bar_dados_biomas


# --------------------------------------
main_graphs = html.Div([
    html.H5("Espécies exclusivas do Brasil",
            style={'text-align': 'center'}),
    html.Div(children=dcc.Graph(
        id='item-1',
        figure=fig1
    )),

    dbc.Row(
        [
            dbc.Col([
                    html.Br(),
                    html.H5("Existência de um Plano Nacional para Conservação (PAN) dentre as espécies exclusivas no Brasil",
                            style={'text-align': 'center'}),
                    dcc.Graph(
                        id='item-4',
                        figure=fig4
                    )]),
            dbc.Col([
                    html.Br(),
                    html.H5("Existência de um Plano Nacional para Conservação (PAN) dentre as espécies não exclusivas no Brasil",
                            style={'text-align': 'center'}),
                    dcc.Graph(
                        id='item-5',
                        figure=fig5
                    )]),
        ]
    ),

    dbc.Row(
        [
            dbc.Col([
                    html.Br(),
                    html.H5("Perfil dos Grupos em relação a exclusividade no Brasil",
                            style={'text-align': 'center'}),
                    dcc.Graph(
                        id='item-2',
                        figure=fig2,
                    )]),
            dbc.Col([
                    html.Br(),

                    html.H5("Perfil dos Biomas em relação a exclusividade no Brasil",
                            style={'text-align': 'center'}),
                    dcc.Graph(
                        id='item-3',
                        figure=fig3
                    )]),
        ]
    ),

    dbc.Row(
        [
            dbc.Col([
                    html.Br(),
                    html.H5("Perfil dos Grupos em relação a presença de um Plano de Ação Nacional Para Conservação",
                            style={'text-align': 'center'}),
                    dcc.Graph(
                        id='item-6',
                        figure=fig6
                    )]),
            dbc.Col([
                    html.Br(),
                    html.H5("Perfil dos Biomas em relação a presença de um Plano de Ação Nacional Para Conservação",
                            style={'text-align': 'center'}),
                    dcc.Graph(
                        id='item-7',
                        figure=fig7
                    )]),
        ]
    ),

    dbc.Row(
        [
            dbc.Col([
                    html.Br(),
                    html.H5("Espécies da Fauna com mais diversidade",
                            style={'text-align': 'center'}),
                    html.H5("de ameaças",
                            style={'text-align': 'center'}),
                    html.Img(id="image_wc_fauna", style={'width': '100%'})
                    ]),
            dbc.Col([
                    html.Br(),
                    html.H5("Espécies da Flora com mais diversidade",
                            style={'text-align': 'center'}),
                    html.H5("de ameaças",
                            style={'text-align': 'center'}),
                    html.Img(id="image_wc_flora", style={'width': '100%'})
                    ]),
        ]
    ),
    # html.Div(children=[
    #     html.Center(html.Div(children=['Espécies da Fauna com mais diversidade de ameaças'], style={
    #                 'font-size': '20px', 'color': '#2a3f5f'}), className='six columns'),
    #     html.Center(html.Div(children=['Espécies da Flora com mais diversidade de ameaças'], style={
    #         'font-size': '20px', 'color': '#2a3f5f'}), className='six columns'),
    # ], className='row'),

    # html.Div(children=[
    #     html.Center(html.Div(children=[
    #         html.Img(id="image_wc_fauna"),
    #     ], className='six columns')),
    #     html.Center(html.Div(children=[
    #         html.Img(id="image_wc_flora"),
    #     ], className='six columns')),
    # ], className='row'),
    # html.Br(),
    # html.H5("Existência de um Plano Nacional para Conservação dentre as espécies não exclusivas no Brasil por Biomas",
    #         style={'text-align': 'center'}),
    # html.Div([
    #     dcc.Dropdown(
    #         id='xaxis-column',
    #         options=[{'label': i, 'value': i}
    #                  for i in dados_biomas['Bioma'].value_counts().index],
    #         value='Cerrado',
    #         clearable=False,
    #
    #     ),
    # ]),
    #
    # html.Div([
    #     dcc.Graph(id='the_graph')
    # ])
])


@ app.callback(Output('image_wc_fauna', 'src'), [Input('image_wc_fauna', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=ameacas_fauna[[
                   'Espécie (Simplificado)', 'total_ameacas']], shape='fauna').save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


@ app.callback(Output('image_wc_flora', 'src'), [Input('image_wc_flora', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=ameacas_flora[[
                   'Espécie (Simplificado)', 'total_ameacas']], shape='flora').save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


# @ app.callback(
#     Output(component_id='the_graph', component_property='figure'),
#     [Input(component_id='xaxis-column', component_property='value')]
# )
# def update_graph(xasis_column_name):
#     fig_teste = go.Figure(data=[go.Pie(labels=dados_biomas.loc[dados_biomas['Bioma'] == xasis_column_name, 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index().index,
#                                        values=dados_biomas.loc[dados_biomas['Bioma'] == xasis_column_name, 'Plano de Ação Nacional para Conservação (PAN)'].value_counts().sort_index(), hole=.4)])
#     fig_teste.update_layout(colorway=[
#                             '#636EFA', '#EF553B'], legend_traceorder='reversed', template="plotly_dark")
#     return (fig_teste)
#     id="satellite-dropdown-component",
#     options=[
#         {"label": "H45-K1", "value": "h45-k1"},
#         {"label": "L12-5", "value": "l12-5"},
#     ],
#     clearable=False,
#     value="h45-k1",
# )


satellite_dropdown_text = html.P(
    id="satellite-dropdown-text", children=["DCA01131", html.Br(), "CIÊNCIA DE DADOS"]
)

satellite_title = html.H1(
    id="satellite-name", children=[
        "Análise das espécies ameaçadas no Brasil"])

satellite_body = html.P(
    className="satellite-description", id="satellite-description", children=["1. Isaac Gomes", html.Br(), "2. Mateus Abrantes", html.Br(), "3. Tales Joabe"]
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        satellite_dropdown_text,
        # html.Div(id="satellite-dropdown", children=satellite_dropdown),
        html.Div(id="panel-side-text",
                 children=[
                     satellite_title,
                    satellite_body,
                 ]),
    ],
)


main_panel_layout = html.Div(
    children=[
        html.Div(id="nav",
                 children=[
                     html.Div(children=[
                         html.Div(children=[
                             html.Img(
                                 src="https://img.icons8.com/cotton/50/000000/footprint-scanning--v1.png"),
                             html.H5('Endangered Species Dashboard', style={
                                 'color': 'white', 'display': 'inline', 'vertical-align': 'middle', "padding-left": "5px", "font-weight": "600"}),
                         ]
                         )]),
                 ], style={'backgroundColor': '#fec036', 'width': '100%', "padding": "10px", "text-align": "center"}),
        html.Div(
            id="panel-upper-lower",
            children=[
                main_graphs,
                map_graph,
                map_biomas,
            ],
        )
    ],
)

app.layout = html.Div([
    html.Div(
        id="root",
        children=[
            side_panel_layout,
            main_panel_layout,
        ],
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
