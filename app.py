'''
this script generates the multipage

the code uses dash pages wich is avaiable from dash version

Dash Pages is available from Dash version 2.5.0.

example from :

https://dash.plotly.com/urls


'''


from dash import Dash, dcc, html, Input, Output, callback

#from pages.assets import imprint

#app = Dash(__name__, use_pages=True)

app = Dash(__name__,use_pages=True) #suppress_callback_exceptions=True

# load content from pages directory
from pages import page1, page2, page3, home

app.title = 'Open Carbonate System Alkalinity Calculations'

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):

    #one subpage
    if pathname == '/page1':
        return page1.layout

    #another subpage
    elif pathname == '/page2':
        return page2.layout

    # another subpage
    elif pathname == '/page3':
        return page3.layout

    # the root page
    elif pathname == '/':
        return home.layout

    elif pathname == '/assets/imprint.html':
        # Read the HTML file
        with open('./assets/imprint.html', 'r') as f:
            html_content = f.read()

        # Using html.Iframe to embed the HTML content
        return html.Iframe(srcDoc=html_content, style={'width': '100%', 'height': '100%'})
    else:
        return '404'


if __name__ == '__main__':
    app.run(debug=True)