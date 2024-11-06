from App.libs import dash, Input, Output, dcc, html, base64, json, State


# Carregar o segundo JSON previamente
with open('E:\\vortex_mods_backup.json', 'r') as file:
    preloaded_json = json.load(file)

app = dash.Dash(__name__, suppress_callback_exceptions=True, meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
])

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a JSON File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False  # Permitir apenas um arquivo
    ),
    html.Div(id='output-data-upload'),
    html.Button('Comparar JSONs', id='compare-button', n_clicks=0),  # Botão de comparação
    html.Div(id='json-compared')
])


# Função para carregar JSON a partir do conteúdo codificado
def load_json_from_upload(content_string):
    decoded = base64.b64decode(content_string)
    return json.loads(decoded)


# Função que compara o JSON carregado com o JSON pré-carregado e retorna os itens sem correspondência
def compare_with_preloaded_json(uploaded_json):
    mods_not_in_preloaded_json = [item for item in uploaded_json if
                                  item['modId'] not in {item['modId'] for item in preloaded_json}]

    if mods_not_in_preloaded_json:
        links = []
        for mod in mods_not_in_preloaded_json:
            link = html.A(
                html.Pre(json.dumps(mod, indent=4)),
                href=mod['link'],
                target="_blank"
            )
            links.append(link)
        return html.Div([
            html.H5("Os seguintes itens do JSON carregado não têm correspondência no JSON pré-carregado:"),
            html.Ul([html.Li(link) for link in links])
        ])
    else:
        return html.Div("Todos os itens do JSON carregado têm correspondência no JSON pré-carregado.")

    # Função que processa o arquivo carregado


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    if 'json' in filename:
        try:
            # Carregar o JSON do arquivo carregado
            uploaded_json = load_json_from_upload(content_string)
            return uploaded_json
        except Exception as e:
            return html.Div([f'Erro ao processar o arquivo {filename}: {str(e)}'])
    else:
        return html.Div([f'O arquivo {filename} não é um JSON.'])


# Callback para salvar o conteúdo do JSON carregado sem realizar a comparação imediatamente
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')],
              )
def update_output(contents, filename):
    if contents is not None:
        return html.Div(f"Arquivo {filename} carregado com sucesso.")
    return html.Div("Por favor, faça upload de um arquivo JSON.")


# Callback para realizar a comparação quando o botão for clicado
@app.callback(Output('json-compared', 'children'),
              [Input('compare-button', 'n_clicks')],
              [State('upload-data', 'contents'),
               State('upload-data', 'filename')])
def compare_jsons(n_clicks, contents, filename):
    if n_clicks > 0 and contents is not None:
        uploaded_json = parse_contents(contents, filename)
        if isinstance(uploaded_json, list):
            return compare_with_preloaded_json(uploaded_json)
        return uploaded_json  # Caso haja erro no parse, ele será retornado aqui
    elif n_clicks > 0 and contents is None:
        return html.Div("Por favor, faça upload de um arquivo JSON antes de comparar.")
    return html.Div("")  # Não exibir nada até que o botão seja clicado


if __name__ == '__main__':
    app.css.config.serve_locally = True
    app.scripts.config.serve_locally = True
    app.run_server(debug=True)
