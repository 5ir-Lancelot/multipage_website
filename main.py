'''
this script generates the multipage

the code uses dash pages wich is avaiable from dash version

Dash Pages is available from Dash version 2.5.0.

example from :

https://dash.plotly.com/urls


'''



import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1('Multi-page app with Dash Pages'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)