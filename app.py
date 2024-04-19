'''
this script generates the multipage

the code uses dash pages wich is avaiable from dash version

Dash Pages is available from Dash version 2.5.0.

example from :

https://dash.plotly.com/urls

Two or more apps might not be needed, maybe only one app can just change the page content. Update comes tomorrow.
'''


from dash import Dash, dcc, html, Input, Output, callback

#from pages.assets import imprint

#app = Dash(__name__, use_pages=True)

# if everything runs well just include the  suppress_callback_exceptions=True

app = Dash(__name__,use_pages=True) #suppress_callback_exceptions=True


# optional design shit for you  Mert in case you can use it
'''

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/flatly/bootstrap.min.css',
                        #'https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/journal/bootstrap.min.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.18.1/styles/monokai-sublime.min.css']


#external_stylesheets=[dbc.themes.CYBORG]


external_scripts = ['https://code.jquery.com/jquery-3.2.1.slim.min.js',
                    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js',
                    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js']

# no clue what these external scripts do
#external_scripts=[dbc.]
# Server definition

server = flask.Flask(__name__)

# layout options
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/




app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                external_scripts=external_scripts,
                server=server,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])

# title taht will be visible in the browser tab
app.title = 'Open Carbonate System Alkalinity Calculations'


# important part of code for the dash pages (to register it)
#dash.register_page(__name__, path='/script')

# for Heroku to regognize it
server=app.server

'''





# load content from pages directory
from pages import  page2, page3, home

app.title = 'Open Carbonate System Alkalinity Calculations'

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])






@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):

    #one subpage
    if pathname == '/page2':
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

    # task for mert : here put the impressum and Datenschutz and Barrierefreiheit etc

    else:
        return '404'


if __name__ == '__main__':
    app.run(debug=True)