# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 14:05:38 2021

@author: watda

the framework used for this python app is Flask

Developers can develop the Python backend framework any way they need, however, it was designed for applications that are open-ended.
Flask has been used by big companies, which include LinkedIn and Pinterest.
Compared to Django, Flask is best suited for small and easy projects.
Thus, you can expect a web server development, support for Google App Engine as well as in-built unit testing.

my app should be tidied up and inspired by Chris one

path to open 


then run it from the console anaconde prompt

python my_app_freshwater.py

how to make it online available:
https://www.youtube.com/watch?v=b-M2KQ6_bM4


1. Open Heroku website and add application   (the name of the app will be part of the url)
2. Open Pycharm Community Verion
3. Create new project in Pycharm Community Verion  choose virtual environment (Virtualenv)
4. copy the files for the app in the folder of the new project 

5. Manually install all necessary packages  to run the python code in the virtual env
    important package used indirectly alwas has to be installed
    + pip install gunicorn    

6.create a requiremnets text file with all the pip install package + version

7. create .gitignore file  (or just copy it from the other projects)
 the gitignore file   is a simple text file with following content:
     venv
     *.pyc
     .env
     .DS_Store
8. create a procfile  with the content 
    web : guincorn  appname_without.py:server
    
9. create a requirements file  (command in the Pycharm terminal)
    this tells heroku which packages are necessary to run the app
    pip freeze > requirements.txt
    
    
10. log in  command in Pycharm
    heroku login

update to generate a simple requirements.txt file that just contains what was used in the given project

menue -> tools -> Synch Python requirements

In the procfile the python file with the real app that should be used need to be specified.
    

    
https://github.com/Vitens/phreeqpython
"""

"""
lukas 04.03.2024

improved version allowing for more input variables (more water parameters)

put a table as input


very important to run a specific file as the main script 
the run command need to be changed on the digitalocean website

go to app -> settings -> commands -> run command -> edit


"""

'''
update implementation on uni website

how the wsgi file should look like:
https://community.plotly.com/t/dash-pythonanywhere-deployment-issue/5062

Mert 06.05.2024 :
Improved the layout of the app and added more functionalities such as switching between table and graph view and footer.

'''

import os
import dash
import dash_bootstrap_components as dbc
import dash_defer_js_import as dji
import flask
import pandas as pd
# import the package for carbonate system calculation chemistry
import phreeqpython
import plotly.graph_objects as go
from dash import dcc, dash_table
from dash import html
from dash.dependencies import Input, Output
from numpy import log10
from plotly.subplots import make_subplots

import numpy as np
from dash.dependencies import Output, Input

#database which should be used for the calculations
# PhreeqPython comes standard with phreeqc.dat, pitzer.dat and vitens.dat
pp = phreeqpython.PhreeqPython(database='vitens.dat')

# different themes (styles of the webpage) can be found here https://bootswatch.com/

# here you can search for a good free bootstrap CND and just copy the link into the external stylesheets and load it
# https://www.bootstrapcdn.com/bootswatch/

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/flatly/bootstrap.min.css',
                        #'https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/journal/bootstrap.min.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.18.1/styles/monokai-sublime.min.css']

external_scripts = ['https://code.jquery.com/jquery-3.2.1.slim.min.js',
                    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js',
                    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js']

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

# for Heroku to regognize it
server=app.server

filepath = os.path.split(os.path.realpath(__file__))[0]

# the "r" refers to read mode
# it need tro be a  raw string  so that the markdown text is properly loaded with all the backslashes

narrative_text = open(os.path.join(filepath, "assets/narrative_improved.md"), "r").read()
refs_text = open(os.path.join(filepath, "assets/references.md"), "r").read()
some_text = open(os.path.join(filepath, "assets/sometext.md"), "r").read()
input_text=open(os.path.join(filepath, "assets/Textbox_input.md"), "r").read()
output_text=open(os.path.join(filepath, "assets/Textbox_output.md"), "r").read()

image_path = 'assets/uhh-logo-web.jpg'

# mathjax is the program translating the Latex MathML with Javascript to generate html to be displayed in the browser
# this path loads automatically the latest version

# loading and configuring mathjax
#https://docs.mathjax.org/en/v2.7-latest/configuration.html

#general style of the app

# how this app.index_string works https://dash.plotly.com/external-resources
# HTML string is customizable but does not need to be customized

app.index_string = '''
<!DOCTYPE html>
<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='en' lang='en'>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            footer {
                left: 0;
                bottom: 0;
                width: 100%;
                background-color: #333;
                color: white;
                text-align: center;
                padding: 10px 0;
            }
            footer a {
                font-size: 16px;
                margin: 0 5px;
                color: white;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
        <a href='/assets/imprint.html'>Impressum</a>
        <a href='/assets/datenschutz.html'>Datenschutz</a>
        <a href='/assets/barrierefreiheitserklaerung.html'>Barrierefreiheit</a>
    </footer>
    </body>
</html>
'''

# COMPONENTS
# ==========
# read in the bjerrum plot csv file as lines
lines=pd.read_table(os.path.join(filepath,"./assets/bjerrum_plot_update_phreeqpython.csv"), sep=',', keep_default_na=False \
                    , na_filter=False, header='infer', engine='python', encoding='utf-8')


DIC_line=pd.read_table(os.path.join(filepath,'./assets/open_carbonate_system_phreeqpython.csv'), sep=',', keep_default_na=False \
                       , na_filter=False, header='infer', engine='python', encoding='utf-8')


# molar mass table
elements=pd.read_csv(os.path.join(filepath,'./assets/Periodic Table of Elements.csv'),sep=',', keep_default_na=False \
                       , na_filter=False, header='infer', engine='python', encoding="utf-8")

# Convert the DataFrame into a dictionary
element_weights = dict(zip(elements['Symbol'], elements['AtomicMass']))


## Interactors
## -----------

#set some constants





M_C=12.011 #g/mol
M_CH4=16.04 #g/mol
M_CO2=44.01 #g/mol
M_CO3=60.01 #g/mol
M_H=1.00784 #g/mol
M_H2=M_H*2 # g/mol
M_H2O=18.01528 #g/mol
M_HCO3=61.0168 # g/mol
M_Na=22.98976928 # g/mol
M_NaCO3=M_CO3+M_Na # g/mol
M_NaHCO3=M_HCO3+M_Na # g/mol
M_OH=17.008 # g/mol
M_NaOH=M_Na+M_OH # g/mol
M_O=15.999 # g/mol
M_O2=M_O*2 # g/mol




M_Mg=24.305 # g/mol
M_Ca=40.078  # g/mol
M_K=39.0983 #g/mol
M_CaCO3=M_Ca+M_C+3*M_O
M_MgCO3=M_Mg+M_C+3*M_O
M_MgHCO3=M_Mg+M_HCO3
M_CaHCO3=M_Ca+M_HCO3


M_CaOH=M_Ca+M_OH

M_MgOH=M_Mg+M_OH

#create the converfrsion dict
conv={'CH4': M_CH4, 'CO2': M_CO2,
      'CO3-2': M_CO3, 'H+': M_H,
      'H2': M_H2,'H2O': M_H2O,
      'HCO3-': M_HCO3, 'Na+':M_Na,
      'NaCO3-': M_NaCO3, 'NaHCO3': M_NaHCO3,
      'NaOH': M_NaOH, 'O2': M_O2, 'OH-':M_OH,
      'Ca+2':M_Ca,'CaCO3':M_CaCO3,
      'Mg+2':M_Mg,'MgCO3':M_MgCO3,
      'MgHCO3+':M_MgHCO3,'MgOH+':M_MgOH,
      'CaHCO3+':M_CaHCO3,'CaOH+':M_CaOH,
      'K+':element_weights['K'],
      'Cl-':element_weights['Cl'],
      'H2S':2*element_weights['H']+element_weights['S'],
      'HS-':element_weights['H']+element_weights['S'],
      'HSO4-':element_weights['H']+element_weights['S']+4*element_weights['O'],
      'CaHSO4+':element_weights['Ca']+element_weights['H']+element_weights['S']+4*element_weights['O'],
      'CaSO4':element_weights['Ca']+element_weights['S']+4*element_weights['O'],
      'KSO4-':element_weights['K']+element_weights['S']+4*element_weights['O'],
      'MgSO4':element_weights['Mg']+element_weights['S']+4*element_weights['O'],
      'NaSO4-':element_weights['Na']+element_weights['S']+4*element_weights['O'],
      'S-2':element_weights['S'],
      'SO4-2':element_weights['S']+4*element_weights['O'],
      'N2':2*element_weights['N'],
      'NH3':element_weights['N']+3*element_weights['H'],
      'NH4+':element_weights['N']+4*element_weights['H'],
      'F-':element_weights['F'],
      'NH4SO4-':element_weights['N']+4*element_weights['H']+element_weights['S']+4*element_weights['O'],
      'NO2-':element_weights['N']+2*element_weights['O'],
      'NO3-':element_weights['N']+3*element_weights['O'],
      'HF':element_weights['H']+element_weights['F'],
      'HF2-':element_weights['H']+2*element_weights['F'],
      'MgF+':element_weights['H']+2*element_weights['F'],
      'NaF':element_weights['Na']+element_weights['F']
      }


#put a whole table here for the input


#set global strings for the variables

TA_s='TAcarb [ueq/kgw]'
T_s='water T [degC]'
pCO2_s='air pCO2 [ppm]'

#cations
Na_s='Na⁺ [umol/kgw]'
Mg_s='Mg²⁺ [umol/kgw]'
Ca_s='Ca²⁺ [umol/kgw]'
K_s='K⁺ [umol/kgw]'

#anions
Cl_s='Cl- [umol/kgw]'
SO4_s='SO₄²- [umol/kgw]'
NO2_s='NO₃⁻ [umol/kgw]'
F_s='F- [umol/kgw]'
PO4_s='PO₄³⁻ [umol/kgw]'




#variables to use for the data input table
params = [TA_s, T_s, pCO2_s]

cations=[Na_s, Mg_s, Ca_s, K_s,]


anions=[Cl_s, SO4_s, NO2_s, F_s]



#set the range for the slider
T_range=[0,80]

T_slider=dcc.Slider(id='T_input', min=T_range[0], max=T_range[1], step=0.5, marks={x: str(x)+'°C' for x in range(T_range[0],T_range[1],10)},
        value=20, tooltip={"placement": "bottom", "always_visible": True}, updatemode='drag')

CO2_value=dcc.Input(
        id='CO2_input',
        placeholder='Insert CO2 value',
        type='number',
        value=415)

alkalinity_value=dcc.Input(
        id='TA_input',
        placeholder='Insert TA value',
        type='number',
        value=2500)
table_composition = "table_composition"


# APP LAYOUT
# ==========
# here the layout of the different pages are defined, these are changed based on the button clicks, could be simplified by keeping the same layout and just changing the content that is different, for now it is kept like this. Mert 06.05.2024
page1_layout = html.Div([
    dbc.Container(children=[
        html.Img(src=image_path, alt='UHH logo rot weiß png'),
        dcc.Markdown(narrative_text, mathjax=True),        
        dbc.Row([
            dbc.Col(dbc.Button("Table", id="btn-page-1", n_clicks=0, color="success", className="flex items-center justify-center my-4", style={'font-size': '1.5em', 'padding': '10px', 'margin': 'auto', 'display': 'block', 'text-align': 'center', 'background-color': '#149c7d', 'pointer-events': 'none', 'width': '100%'})),
            dbc.Col(dbc.Button("Graph", id="btn-page-2", n_clicks=0, color="success", className="flex items-center justify-center my-4", style={'font-size': '1.5em', 'padding': '10px', 'margin': 'auto', 'display': 'block', 'text-align': 'center', 'width': '100%'}))
        ]),
        #input whole editable data table
        html.Br(),
        html.H2('Input tables :'),
        html.B('Enter all the observed parameters here in this table. Default is starting with 0 for everything (closed system with pure water):'),
        html.Br(),
        html.Br(),
        dcc.Markdown(input_text,mathjax=True),
        html.Br(),
        html.H2('Basic parameters :'),
        dash_table.DataTable(
                id='table-bulk',
                columns=(
                    [{'id': 'Model', 'name': 'sample'}] +
                    [{'id': p, 'name': p} for p in params]
                ),
                data=[
                    dict(Model=i, **{param: 0 for param in params})
                    for i in range(1, 2)
                ],
                editable=True,
                #make some color code for the columns with zero
                style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{'+TA_s+'}=0',
                                'column_id': TA_s
                            },
                            'backgroundColor': 'tomato',
                            'color': 'black'
                        },
                        {
                            'if': {
                                'filter_query': '{'+T_s+'}=0',
                                'column_id': T_s
                            },
                            'backgroundColor': 'tomato',
                            'color': 'black'
                        },
                        {
                            'if': {
                                'filter_query': '{' + pCO2_s + '}=0',
                                'column_id': pCO2_s
                            },
                            'backgroundColor': 'tomato',
                            'color': 'black'
                        }

                    ]
            ),
        html.Br(),
        html.H2('Cations :'),
        dash_table.DataTable(
                        id='table-cations',
                        columns=(
                            [{'id': 'Model', 'name': 'sample'}] +
                            [{'id': p, 'name': p} for p in cations]
                        ),
                        data=[
                            dict(Model=i, **{param: 0 for param in cations})
                            for i in range(1, 2)
                        ],
                        editable=True,
                        #make some color code for the columns with zero
                        style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{'+Na_s+'}=0',
                                        'column_id': Na_s
                                    },
                                    'backgroundColor': 'tomato',
                                    'color': 'black'
                                },
                                {
                                    'if': {
                                        'filter_query': '{'+Mg_s+'}=0',
                                        'column_id': Mg_s
                                    },
                                    'backgroundColor': 'tomato',
                                    'color': 'black'
                                },
                                {
                                    'if': {
                                        'filter_query': '{'+Ca_s+'}=0',
                                        'column_id': Ca_s
                                    },
                                    'backgroundColor': 'tomato',
                                    'color': 'black'
                                },
                                {
                                    'if': {
                                        'filter_query': '{' + Ca_s + '}=0',
                                        'column_id': Ca_s
                                    },
                                    'backgroundColor': 'tomato',
                                    'color': 'black'
                                },
                                {
                                    'if': {
                                        'filter_query': '{' + K_s + '}=0',
                                        'column_id': K_s
                                    },
                                    'backgroundColor': 'tomato',
                                    'color': 'black'
                                }

                            ]
                    ),
        html.Br(),
        html.H2('Anions :'),
        html.Br(),
        dash_table.DataTable(
                                id='table-anions',
                                columns=(
                                    [{'id': 'Model', 'name': 'sample'}] +
                                    [{'id': p, 'name': p} for p in anions]
                                ),
                                data=[
                                    dict(Model=i, **{param: 0 for param in anions})
                                    for i in range(1, 2)
                                ],
                                editable=True,
                                #make some color code for the columns with zero
                                style_data_conditional=[
                                        {
                                            'if': {
                                                'filter_query': '{'+Cl_s+'}=0',
                                                'column_id': Cl_s
                                            },
                                            'backgroundColor': 'tomato',
                                            'color': 'black'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{'+SO4_s+'}=0',
                                                'column_id': SO4_s
                                            },
                                            'backgroundColor': 'tomato',
                                            'color': 'black'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{'+NO2_s+'}=0',
                                                'column_id': NO2_s
                                            },
                                            'backgroundColor': 'tomato',
                                            'color': 'black'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{' + F_s + '}=0',
                                                'column_id': F_s
                                            },
                                            'backgroundColor': 'tomato',
                                            'color': 'black'
                                        },

                                    ]
                            ),

        html.Br(),
        html.H2('Output tables :'),
        html.Br(),

        html.B('This is the resulting speciation after the water is in equilibrium with the atmosphere:'),
        html.Br(),
        html.Br(),
        html.Div(id="table1", style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'middle'}),
        html.Br(),
        html.Br(),
        html.B('Those are the saturation indices of minerals that can precipitate:'),
        html.Plaintext('When the water sample reaches over-saturation the certain mineral will be highlighted in red.'),
        html.Br(),
        html.Br(),
        html.Div(id="table2", style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'middle'}),
        html.Br(),
        html.Br(),
        html.B('Bulk parameters:'),
        html.Br(),
        html.Br(),
        html.Div(id="table3", style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'middle'}),
        html.Br(),
        html.Br(),
        dcc.Markdown(some_text,mathjax=True),
        
        
        
        dcc.Markdown(refs_text,mathjax=True),
        html.Br(),

    ]),
], style={'fontSize': '1.2em'}) # global font size setting
page2_layout = html.Div([
    dbc.Container(children=[
        html.Img(src=image_path, alt='UHH logo rot weiß png'),
        dcc.Markdown(narrative_text, mathjax=True),
        dbc.Row([
            dbc.Col(dbc.Button("Table", id="btn-page-1", n_clicks=0, color="success", className="flex items-center justify-center my-4", style={'font-size': '1.5em', 'padding': '10px', 'margin': 'auto', 'display': 'block', 'text-align': 'center', 'width': '100%'})),
            dbc.Col(dbc.Button("Graph", id="btn-page-2", n_clicks=0, color="success", className="flex items-center justify-center my-4", style={'font-size': '1.5em', 'padding': '10px', 'margin': 'auto', 'display': 'block', 'text-align': 'center', 'width': '100%', 'background-color': '#149c7d', 'pointer-events': 'none'}))
        ]),
        #dcc.Graph(id="sir_solution", figure=display_SIR_solution(solve(delta=0.5, R0=2.67, tau=8.5))),
        
        html.Br(),
        dbc.Row(children=[dbc.Col(children=["water tempearture [°C]:"], className="col-md-4"),
                          dbc.Col(children=[T_slider], className="col-md-8")]),
        html.Br(),
        dbc.Row(children=[dbc.Col(children=["CO2 partial pressure to equilibrate with [ppm]:"], className="col-md-4"),
                          dbc.Col(children=[CO2_value], className="col-md-8")]),
        html.Br(),
        dbc.Row(children=[dbc.Col(children=["Total Alkalinity [ueq/L] :"], className="col-md-4"),
                          dbc.Col(children=[alkalinity_value], className="col-md-8")]),
        html.Br(),
        html.Br(),
        dcc.Graph(id="indicator-graphic", style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'middle', 'height': '150vh'}),
        # old settings
        # 'height': '90vh'
        # , 'display': 'inline-block', 'vertical-align': 'middle'
        
        #stuff for another diagram
# =============================================================================
#         dbc.Row(children=[dbc.Col(children=["Temp [°C]"], className="col-md-4"),
#                           dbc.Col(children=[T_slider2], className="col-md-8")]),
#         dcc.Graph(id='temperature'),
# =============================================================================
        html.Br(),
        html.B('This is the resulting speciation after the water is in equilibrium with the atmosphere:'),
        html.Br(),
        html.Br(),
        
        #html.Table([
        #html.Tr(['species]
        #html.Tr([html.Td(['CO2(aq)= ']), html.Td(id='CO2_species'), html.Td("[umol/l]")   ]  ),
        #html.Tr([html.Td(['HCO3- = ']), html.Td(id='HCO3_species'), html.Td("[umol/l]") ]),
        #html.Tr([html.Td(['CO3-2 = ']), html.Td(id='CO3_species'), html.Td("[umol/l]") ]),
        #html.Tr([html.Td(['Na+   = ']), html.Td(id='Na_species'), html.Td("[umol/l]") ]),
        #html.Tr([html.Td(['H+    = ']), html.Td(id='H_species'), html.Td("[umol/l]") ]),
        #html.Tr([html.Td(['OH-  =   ']), html.Td(id='OH_species'), html.Td("[umol/l]") ]),
        #html.Tr([html.Td(['NaCO3- =   ']), html.Td(id='NaCO3_species'), html.Td("[umol/l]") ]),
        #]),
        
        html.Div(id=("%s" % table_composition), style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'middle'}),
        html.Br(),
        html.Br(),

        dcc.Markdown(some_text, dangerously_allow_html=True),
        
        
        
        dcc.Markdown(refs_text, dangerously_allow_html=True),
        html.Br(),
    ]),
], style={'fontSize': '1.2em'}) # global font size setting)
#
# INTERACTION
# ===========
# here inputs and outputs of the application are defined

@app.callback(
    [Output("table1", "children"),
     Output("table2", "children"),
     Output("table3", "children")],
    [Input('table-bulk', 'data'), #1 bulk table
     Input('table-bulk', 'columns'), #1 bulk table
     Input('table-cations', 'data'), #2 cation table
     Input('table-cations', 'columns'),  # 2 cation table
     Input('table-anions', 'data'), #3 anion table
     Input('table-anions', 'columns')], #2 anion table
)


def update_graph(bulk_data, bulk_columns, cations_data, cations_columns, anions_data, anions_columns):

        #merge data inputs
        # Process input tables into DataFrames
        df_bulk = pd.DataFrame(bulk_data, columns=[col['name'] for col in bulk_columns])
        df_cations = pd.DataFrame(cations_data, columns=[col['name'] for col in cations_columns])
        df_anions = pd.DataFrame(anions_data, columns=[col['name'] for col in anions_columns])

        # Ensure all DataFrames are numeric (float)
        df_bulk = df_bulk.apply(pd.to_numeric, errors='coerce')
        df_cations = df_cations.apply(pd.to_numeric, errors='coerce')
        df_anions = df_anions.apply(pd.to_numeric, errors='coerce')

        # Combine all DataFrames into a single one
        df = pd.concat([df_bulk, df_cations, df_anions], axis=1)

        # getting all the data from the input table
        #df = pd.DataFrame(rows, columns=[c['name'] for c in columns])

        #make whole dataframe to float
        #df = df.apply(pd.to_numeric, errors='coerce')

        #define output table

        #df_out=

        #solution function can just take single numbers so we use a for loop

        #when all input is zero it is fine

        for k in df.index:

            # TA_s, T_s, pCO2_s, Na_s,
            #     Mg_s, Ca_s]
            sol = pp.add_solution({'units': 'umol/kgw',
                                #'pH': pH,
                                'density': 1.000,
                                'temp': df.loc[k,T_s],
                                # include the cations
                                #'Li': np.nan_to_num(cat[('IC_Ca', '[umol_l]')]),
                                'Na': np.nan_to_num(df.loc[k,Na_s]),
                                #'N(-3)': np.nan_to_num(cat[('IC_NH4', '[umol_l]')]),  # N(-3) stands for NH4
                                'K': np.nan_to_num(df.loc[k,K_s]),
                                'Ca': np.nan_to_num(df.loc[k,Ca_s]),
                                'Mg': np.nan_to_num(df.loc[k,Mg_s]),
                                # include the anions
                                'F': np.nan_to_num(df.loc[k,F_s]),
                                'Cl': np.nan_to_num(df.loc[k,Cl_s]),
                                'N(3)': np.nan_to_num(df.loc[k,NO2_s]),  # N(-3) stands for NO2-
                                'S': np.nan_to_num(df.loc[k, SO4_s]),   # S will be recognized as SO4  in the vitens.dat database
                                # enter total inorganic carbon (C or C(4))
                                # include CO2 as carbon (IV) oxide  (CO2) all C in the configuration
                                # 'C(4)':DIC,
                                # test different notation
                                #'C(4)': DIC,
                                #enter the alklainity (as CO3)
                                'Alkalinity':np.nan_to_num(df.loc[k,TA_s]), # phreeqc adds alkalinity as carbonate alkalinity
                                })

            #closed system case no CO2 interaction
            if np.nan_to_num(df.loc[k,pCO2_s])<=0.0:
                # pH of the solution
                pH = sol.pH

                # Specific conductance, microsiemens per centimeter.
                SC = sol.sc

                # DIC of the solution
                DIC = (sol.total('CO2', units='mol') + sol.total('HCO3', units='mol') + sol.total('CO3',
                                                                                                units='mol'))  # convert it to mol


            else:
                # the pressure default unit is atm so I convert the ppm to atm
                p=df.loc[k,pCO2_s]*1e-6

                # the function equilizie needs the phreeqc input the partial pressure in negative log10 scale

                input_pCO2=log10(p)


                # new function from phreeqc package used this time
                # reaction with ambient CO2 pressure
                sol.equalize(['CO2(g)'], [input_pCO2])

                # pH of the solution
                pH = sol.pH

                # Specific conductance, microsiemens per centimeter.
                SC = sol.sc

                # DIC of the solution
                DIC = (sol.total('CO2', units='mol') + sol.total('HCO3', units='mol') + sol.total('CO3',units='mol'))  # convert it to mol

        #after reaction generate the output

        #get concentration of all species
        df=pd.DataFrame.from_dict(sol.species, orient='index', columns=['concentration [mol/kgw]'])

        df = df.rename_axis(['species']).reset_index()


        # dict comprehension {k: prices[k]*stock[k] for k in prices}

        df['concentration [mg/kgw]']={key: 1000*value*conv[key] for key,value in sol.species.items()}.values()

        df['concentration [ppm]'] = {key: 1000 * value * conv[key] for key, value in sol.species.items()}.values()
        #format = Format(precision=4, scheme=Scheme.fixed)


        #dash table object

        tbl1=dash_table.DataTable(
            id="format_table",
            columns=[
                {
                    "name": i,
                    "id": i,
                    "type": "numeric",  # Required!
                    'format': dash_table.Format.Format(precision=4, scheme=dash_table.Format.Scheme.exponent)
                }
                for i in df.columns
            ],
            data=df.to_dict("records"),
            editable=True,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '100%'},
        )

        #output the saturation index table

        df_phases=pd.DataFrame.from_dict(sol.phases, orient='index', columns=['saturation index (SI)'])

        df_phases = df_phases.rename_axis(['mineral']).reset_index()

        df_phases['IAP/Ksp']=10**df_phases['saturation index (SI)']
        # get SI of the phases


        tbl2 = dash_table.DataTable(
            id="format_table",
            columns=[
                {
                    "name": i,
                    "id": i,
                    "type": "numeric",  # Required!
                    'format': dash_table.Format.Format(precision=4, scheme=dash_table.Format.Scheme.exponent)
                }
                for i in df_phases.columns
            ],
            data=df_phases.to_dict("records"),
            editable=True,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '100%'},
            style_data_conditional=[

                {
                    'if': {
                        'filter_query': '{saturation index (SI)} >0',
                        'column_id': 'saturation index (SI)'
                    },
                    'backgroundColor': 'tomato',
                    'color': 'white'
                },

                {
                    'if': {
                        'filter_query': '{IAP/Ksp} >1',
                        'column_id': 'IAP/Ksp'
                    },
                    'backgroundColor': 'tomato',
                    'color': 'white'
                },

            ]
        )


        #
        #

        # calculate DIC


        d={'Dissolved inorganic carbon [mol/kgw]':[DIC],'pH':[pH],'EC [uS/cm]':[SC]}

        df_extra=pd.DataFrame.from_dict(d,orient='index',columns=['number'])

        df_extra = df_extra.rename_axis(['variable']).reset_index()



        tbl3 = dash_table.DataTable(
            id="format_table",
            columns=[
                {
                    "name": i,
                    "id": i,
                    "type": "numeric",  # Required!
                    'format': dash_table.Format.Format(precision=4, scheme=dash_table.Format.Scheme.exponent)
                }
                for i in df_extra.columns
            ],
            data=df_extra.to_dict("records"),
            editable=True,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '100%'},

        )




        return tbl1, tbl2,tbl3


@app.callback(
    [Output("indicator-graphic", "figure"),
     Output(table_composition, "children")],
    [Input("T_input", "value"),
     Input("CO2_input", "value"),
     Input("TA_input", "value")],
)


def update_graph_2(T_input,CO2_input,TA_input):

    # Helper function to sanitize input to make sure that commas dont cause error (the ',' will just be removed)
    # the real decimal seperator '.' will be accepted
    def sanitize_input(input_value):
        #print(f"Sanitizing input: {input_value}")

        if input_value is None:
            #print("Input is None")
            return None

        # Check if the input is already a number (either float or int)
        if isinstance(input_value, (int, float)):
            #print(f"Input is already a number: {input_value}")
            return float(input_value)

        try:
            # Replace commas with empty strings to handle cases like "1,000"
            sanitized_value = float(input_value.replace(",", ""))
            #print(f"Sanitized value: {sanitized_value}")
            return sanitized_value
        except (ValueError, AttributeError) as e:
            #print(f"Failed to sanitize input: {e}")
            return None

    # Sanitize all inputs
    T = sanitize_input(T_input)
    CO2 = sanitize_input(CO2_input)
    TA = sanitize_input(TA_input)

    # Check if any input is invalid
    if T is None or CO2 is None or TA is None:
        # Return fallback outputs for invalid inputs
        figure = {
            "data": [],
            "layout": {
                "title": "Oops! Something Went Wrong",
                "annotations": [{
                    "text": "Uh-oh, looks like you've entered something funky!<br>Please double-check your inputs.<br>Remember: use '.' for decimals and skip the ','s.",
                    "font": {"size": 30, "color": "red"},  # Red color for annotation text
                    "x": 2.5,  # Center the annotation
                    "y": 3.5,  # Place it towards the top
                    "showarrow": False
                }]
            }
        }

        # Customize the text size, position, and color for the HTML message
        table = html.Div([
            html.Div(
                "Uh-oh, looks like you've entered something funky! Please double-check your inputs. Remember: use '.' for decimals and skip the ','s.",
                style={
                    'fontSize': '24px',  # Make the font larger
                    'textAlign': 'center',  # Center the text
                    'marginTop': '20px',  # Add some space at the top
                    'color': 'red'  # Make the text red
                }
            )
        ])
        return figure, table

    else:


        # removed log scale
        alk=TA
        
        #convert umol/L concentartion in mmol/L  
        c=alk*1e-3


        sol=pp.add_solution_simple({'NaHCO3':c},temperature=T) # in Phreeqc default units are mmol/kgw
        
        
        # the pressure default unit is atm so I convert the ppm to atm
        p=CO2*1e-6
        
        # the function equilizie needs the phreeqc input the partial pressure in negative log10 scale

        input_pCO2=log10(p)
        

        # new function from phreeqc package used this time
        # reaction with ambient CO2 pressure
        sol.equalize(['CO2(g)'], [input_pCO2])
        
        

        #plotly command for plots
        # very simple plot that already works 
        #fig= px.line(x=np.linspace(0, 10, 1000),y=T*np.linspace(0, 10, 1000))
        
        #line break in plotly strings <br>
        
        #marker_color defines the different bar colors (it can be also dependent on paramameters, continiuos or distinct)
        # the numbers refer to different colors ( I dont know the exact colors)

        # Lukas change rows and columns to stack the plots below each other and not side by side

        fig = make_subplots(rows=3, cols=1, subplot_titles=('Inorganic carbon components <br> in the solution','DIC(T,CO2_atm,pH)',
                                                        "Fractions of <br> DIC(T,CO2_atm,pH)") ,column_widths=[1])
        
        # all possible layout settings
        # https://plotly.com/python/reference/layout/
        
        fig.update_layout(
                font_family="Courier New",
                font_size=20,
                font_color="black",
                title_font_family="Courier New",
                title_font_size=29,
                title_font_color="red",
                legend_title_font_color="green",
                #height=1800, # global plot height
                #width='90vh', # dynamic plot width (adjusted to browser window)u
                title_text="Equilibrium Solution for pure Carbonate System",
                #legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                )
        

        #
        x_bar=['HCO<sub>3</sub><sup>-</sup><sub>(aq)','CO<sub>3</sub><sup>2-</sup><sub>(aq)','CO<sub>2</sub><sub>(aq)','H<sup>+</sup>','OH<sup>-</sup>']
        html.Div(["H", html.Sub(2), "H", html.Sup(2)])
        
        # a=sol.total('HCO3')

        #b=sol.total('CO3')

        #c=sol.total('CO2')

        #get the total dissolved inorganc carbon
        #sol.total_element('C', units='mmol')
        
        
        # print(solution.species['HCO3-'])
        # everything in umol/l

        #for species the output is mol

        #also add H+ and OH-

        y_bar=[sol.total('HCO3')*1000,sol.total('CO3')*1000,sol.total('CO2')*1000,sol.species['H+']*1e6,sol.species['OH-']*1e6]
        
        water_type=['freshwater']  # here one can add freshwater etc if it would be interesting in this case
        
        fig.add_trace(go.Bar(name='aqueus composition', x=x_bar, y=y_bar),row=3, col=1)
        
        #fig.add_trace(go.Bar(name=x_bar[1], x=['CO3'], y=[y_bar[1]],width=2),row=3, col=1)
        
        #fig.add_trace(go.Bar(name=x_bar[2], x=['CO2(aq)'], y=[y_bar[2]],width=2),row=3, col=1)

        #fig.add_trace(go.Bar(name=x_bar[4], x=['H+'], y=[y_bar[4]],width=2), row=3, col=1)

        #fig.add_trace(go.Bar(name=x_bar[5], x=['OH-'], y=[y_bar[5]],width=2), row=3, col=1)

        #update label of the yaxis
        fig.update_yaxes(title_text='c [umol/L]', row=3, col=1)


        #pls work
        
        # Change the bar mode
        #fig.update_layout(barmode='stack')
        


        
        # attention range is in log so 10^0  to 10^6
        
        
        
        
        # create DIC plot from the input data
        fig.add_trace(go.Scatter(x=DIC_line['pH'], y=DIC_line['DIC'], mode='lines+markers', name='DIC reference <br> 415ppm , 25°C'), row=2, col=1)


        #add a single point (pH,DIC) of the real simulation
        # pH of the solution
        pH = sol.pH

        # DIC of the solution
        DIC = (sol.total('CO2',units='mol')+sol.total('HCO3',units='mol')+sol.total('CO3',units='mol')) #convert it to mol

        #make the etxra dot for the current DIC value. Mert: Changed slightly the size of the dot
        fig.add_trace(go.Scatter(x=[pH], y=[DIC], mode='markers', name='DIC solution', marker=dict(
                color='LightSkyBlue',
                size=15,
                line=dict(
                    color='MediumPurple',
                    width=5))
                                ), row=2, col=1)


        # make annotation at the value slighly shiftet in the left. Mert: Modified this so it does not get blocked by the plot
        fig.add_annotation(
            text="pH={:.2f} <br> DIC={:.6f} mol/l <br> DIC={:.6f} g/l <br> DIC= {:.6f} ppm".format(pH, DIC, DIC * M_C, DIC * M_C * 1000),
            showarrow=False,
            xref="paper",  # Use paper coordinates for horizontal positioning
            yref="paper",  # Use paper coordinates for vertical positioning
            x=pH-2,  # Adjust the x-coordinate for horizontal positioning
            y=0.95,  # Adjust the y-coordinate for vertical positioning
            row=2, col=1
        )

        # marker style
        # marker=dict(
        #             color='LightSkyBlue',
        #             size=120,
        #             line=dict(
        #                 color='MediumPurple',
        #                 width=12
        #             )
        #         )

        fig.update_yaxes(title_text="concentration C [mol/L]",type='log', row=2, col=1)

        #fig.add_trace(go.Bar(name=x_bar[0], x=['DIC'], y=[y_bar[0]]),row=2, col=1)
        #fig.update_yaxes(range=[0,10000],row=2, col=1)


        # add trace will add multiple independent lines
        # row and col so determine where to put the plots


        # add the last plot
    
        # input is the array and then it is defined which columns are x and y
    
        fig.add_trace(go.Scatter(x=lines['pH'],y=lines['CO2_frac'],  mode='lines+markers',name=x_bar[2] ),row=1, col=1)
        fig.add_trace(go.Scatter(x=lines['pH'],y=lines['HCO3_frac'], mode='lines+markers',name=x_bar[0] ),row=1, col=1)
        fig.add_trace(go.Scatter(x=lines['pH'],y=lines['CO3_frac'], mode='lines+markers',name=x_bar[1]),row=1, col=1)

        
        
        fig.update_yaxes(title_text="Fraction in decimal ",title_standoff =4, ticksuffix='', row=1, col=1)
        
        fig.update_xaxes(title_text="pH", row=1, col=1)
        
        #pH of the solution
        pH=sol.pH
        
        # electrical conductivity of the solution
        # SC
        

        # Specific conductance, microsiemens per centimeter. 
        SC=sol.sc
        
        
        
        # Add shapes
        # draw pH line and make an annotation
        fig.update_layout(
                shapes=[
                        #draw a shape in the third plot   
                        #the reference is the second xref yref
                        dict(type="line", xref="x3", yref='y3',
                                x0=pH, y0=0, x1=pH, y1=1),])
        
        fig.add_annotation(x=12, y=0.7,
                text="pH={:.2f} <br> EC={:.2f} uS/cm".format(pH,SC),
                showarrow=False,
                yshift=1,row=1, col=1)
        
        #get the concentrations of all the  species in the system

        #get concentration of all species
        df=pd.DataFrame.from_dict(sol.species, orient='index', columns=['concentration [mol/L]'])

        df = df.rename_axis(['species']).reset_index()


        # dict comprehension {k: prices[k]*stock[k] for k in prices}

        df['concentration [mg/L]']={key: 1000*value*conv[key] for key,value in sol.species.items()}.values()

        df['concentration [ppm]'] = {key: 1000 * value * conv[key] for key, value in sol.species.items()}.values()
        #format = Format(precision=4, scheme=Scheme.fixed)


        #dash table object

        tbl=dash_table.DataTable(
            id="format_table",
            columns=[
                {
                    "name": i,
                    "id": i,
                    "type": "numeric",  # Required!
                    'format': dash_table.Format.Format(precision=4, scheme=dash_table.Format.Scheme.exponent)
                }
                for i in df.columns
            ],
            data=df.to_dict("records"),
            editable=True,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '100%'},
        )
        #alka_str='You have selected TA={:.2f} [ueq/L]'.format(alk)

        #fig.update_layout(height=600, width=800, title_text=r"$\alpha Simulation of Dissolved Carbon Dioxide <br> (assume open system in equilibrium) <br> <br>$")

        #it is not possible to add latex in interactive dash

        #the ouputs are arranged in the way like the app.callback function defines them
        # the order has to be followed strictly
        # here i have added c = alkalinity

        # use the dash table  for the html output https://dash.plotly.com/datatable


        return fig,tbl

# Initial page layout
app.layout = html.Div([
    html.Div(id='page-content', children=page1_layout),
])

# Define the callback for updating the page content based on the button clicks
@app.callback(
    Output('page-content', 'children'),
    [Input('btn-page-1', 'n_clicks'),
     Input('btn-page-2', 'n_clicks')]
)
def render_content(btn_page_1, btn_page_2):
    ctx = dash.callback_context
    if not ctx.triggered:
        return page1_layout
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-page-1':
            return page1_layout
        elif button_id == 'btn-page-2':
            return page2_layout


if __name__ == '__main__':
    app.run_server(debug=False)
