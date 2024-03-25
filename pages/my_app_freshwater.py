# -*- coding: utf-8 -*-
'''
new file for the multipage website



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

#database which should be used for the calculations
# PhreeqPython comes standard with phreeqc.dat, pitzer.dat and vitens.dat
pp = phreeqpython.PhreeqPython(database='vitens.dat')



#from components import solve

#from components import solve

# different themes (styles of the webpage) can be found here https://bootswatch.com/

# here you can search for a good free bootstrap CND and just copy the link into the external stylesheets and load it
# https://www.bootstrapcdn.com/bootswatch/

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
dash.register_page(__name__, path='/script')

# for Heroku to regognize it
server=app.server

filepath = os.path.split(os.path.realpath(__file__))[0]

print(filepath)

narrative_text = open(os.path.join(filepath, "../assets/narrative_improved.md"), "r").read()
refs_text = open(os.path.join(filepath, "../assets/references.md"), "r").read()
some_text = open(os.path.join(filepath, "../assets/sometext.md"), "r").read()
#input_text=open(os.path.join(filepath, "assets/Textbox_input.md"), "r").read()
#output_text=open(os.path.join(filepath, "assets/Textbox_output.md"), "r").read()

image_path = '../assets/uhh-logo-web.jpg'

app.index_string = '''
<!DOCTYPE html>
<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='en' lang='en'>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# COMPONENTS
# ==========

# to navigate back  use ././

# read in the bjerrum plot csv file as lines
lines=pd.read_table("././assets/bjerrum_plot_update_phreeqpython.csv", sep=',', keep_default_na=False \
                    , na_filter=False, header='infer', engine='python', encoding='utf-8')


DIC_line=pd.read_table('././assets/open_carbonate_system_phreeqpython.csv', sep=',', keep_default_na=False \
                       , na_filter=False, header='infer', engine='python', encoding='utf-8')




## Interactors
## -----------

#set the ranges for the sliders
T_range=[0,80]
CO2_range=[1,300000]
alkalinity_range=[1,1e+6]

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

#create the convefrsion dict
conv={'CH4': M_CH4, 'CO2': M_CO2,
      'CO3-2': M_CO3, 'H+': M_H,
      'H2': M_H2,'H2O': M_H2O,
      'HCO3-': M_HCO3, 'Na+':M_Na,
      'NaCO3-': M_NaCO3, 'NaHCO3': M_NaHCO3,
      'NaOH': M_NaOH, 'O2': M_O2, 'OH-':M_OH}


T_slider=dcc.Slider(id='T_input', min=T_range[0], max=T_range[1], step=0.5, marks={x: str(x)+'°C' for x in range(T_range[0],T_range[1],10)},
        value=20, tooltip={"placement": "bottom", "always_visible": True}, updatemode='drag')

#
# CO2_slider=dcc.Slider(id='CO2_input', min=CO2_range[0], max=CO2_range[1], step=1, marks={x: str(x)+'ppm' for x in range(CO2_range[0],CO2_range[1],10000)},
#         value=415, tooltip={"placement": "bottom", "always_visible": True}, updatemode='drag')
#

CO2_value=dcc.Input(
        id='CO2_input',
        placeholder='Insert CO2 value',
        type='number',
        value=415)

# alkalinity_slider=dcc.Slider(id='alkalinity_input', min=log10(alkalinity_range[0]) ,max=log10(alkalinity_range[1]), step=0.01,
#         marks={x: '{:.0e}'.format(10**x)+' ueq/L' for x in range(0,6,int(1))},value=log10(2500),
#         tooltip={"placement": "bottom", "always_visible": True},
#         updatemode='drag',drag_value=3)


alkalinity_value=dcc.Input(
        id='TA_input',
        placeholder='Insert TA value',
        type='number',
        value=2500)


T_slider2=dcc.Slider(id='T', min=0, max=100, step=0.5, marks={x: str(x)+'°C' for x in range(0,100,10)},
        value=5, tooltip={"placement": "bottom", "always_visible": True}, updatemode='drag')


# APP LAYOUT
# ==========

layout = html.Div([
    dbc.Container(children=[
        html.Img(src=image_path, alt='UHH logo red white png'),
        dcc.Markdown(narrative_text, mathjax=True),
        
        #dcc.Graph(id="sir_solution", figure=display_SIR_solution(solve(delta=0.5, R0=2.67, tau=8.5))),
        
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
        dcc.Graph(id='indicator-graphic',style={'width': '80vw', 'height':1500}),
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

        html.Div(id="table1", style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'middle'}),
        html.Br(),
        html.Br(),

        dcc.Markdown(some_text, dangerously_allow_html=True),
        
        
        
        dcc.Markdown(refs_text, dangerously_allow_html=True),
        html.Br(),
        #include reference to impressum and data policy
        html.H2('Impressum'),
        html.A('Impressum', href='/assets/imprint.html'),
        html.Br(),
        html.Br(),
        html.H2('Datenschutz'),
        html.A('Datenschutzerklaerung', href='/assets/datenschutz.html'),
        html.Br(),
        html.Br(),
        html.H2('Barrierefreiheit'),
        html.A('Barrierefreiheitserklaerung', href='/assets/barrierefreiheitserklaerung.html'),
        html.Br(),
        html.Br(),
        html.H2('Test'),
        html.A('Lol', href='/page.html'),
         
        
        
    ]),
], style={'fontSize': '1.2em'}) # global font size setting)
    



# INTERACTION
# ===========
# here inputs and outputs of the application are defined

# change here
@app.callback(Output("indicator-graphic", "figure"),
              Output("table1","children"),

              # new output plot include here 18.10.2022

              
              [Input("T_input", "value"),
               Input("CO2_input", "value"),
               Input("TA_input", "value")]
              ) 





def update_graph(T,pCO2,alkalinity):
    
    
    # removed log scale
    alk=alkalinity
    
    #convert umol/L concentartion in mmol/L  
    c=alk*1e-3


    sol=pp.add_solution_simple({'NaHCO3':c},temperature=T) # in Phreeqc default units are mmol/kgw
    
    
    # the pressure default unit is atm so I convert the ppm to atm
    p=pCO2*1e-6
    
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
    x_bar=['DIC','HCO<sub>3</sub><sup>-</sup><sub>(aq)','CO<sub>3</sub><sup>-2</sup><sub>(aq)','CO<sub>2</sub><sub>(aq)','H<sup>+</sup>','OH<sup>-</sup>']
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

    y_bar=[sol.total_element('C', units='mmol')*1000,sol.total('HCO3')*1000,sol.total('CO3')*1000,sol.total('CO2')*1000,sol.species['H+']*1e6,sol.species['OH-']*1e6]
    
    water_type=['freshwater']  # here one can add freshwater etc if it would be interesting in this case
    
    fig.add_trace(go.Bar(name=x_bar[3], x=water_type, y=[y_bar[3]]),row=1, col=1) 
    
    fig.add_trace(go.Bar(name=x_bar[1], x=water_type, y=[y_bar[1]]),row=1, col=1)
    
    fig.add_trace(go.Bar(name=x_bar[2], x=water_type, y=[y_bar[2]]),row=1, col=1)

    fig.add_trace(go.Bar(name=x_bar[4], x=water_type, y=[y_bar[4]]), row=1, col=1)

    fig.add_trace(go.Bar(name=x_bar[5], x=water_type, y=[y_bar[5]]), row=1, col=1)

    #update label of the yaxis
    fig.update_yaxes(title_text='c [ueq/L]', row=1, col=1)


    #pls work
    
    # Change the bar mode
    fig.update_layout(barmode='stack')
    


    
    # attention range is in log so 10^0  to 10^6
    
    
    
    
     # create DIC plot from the input data
    fig.add_trace(go.Scatter(x=DIC_line['pH'], y=DIC_line['DIC'], mode='lines+markers', name='DIC reference <br> 415ppm , 25°C'), row=2, col=1)


    #add a single point (pH,DIC) of the real simulation
    # pH of the solution
    pH = sol.pH

    # DIC of the solution
    DIC = (sol.total('CO2',units='mol')+sol.total('HCO3',units='mol')+sol.total('CO3',units='mol')) #convert it to mol

    #make the etxra dot for the current DIC value
    fig.add_trace(go.Scatter(x=[pH], y=[DIC], mode='markers', name='DIC solution', marker=dict(
            color='LightSkyBlue',
            size=50,
            line=dict(
                color='MediumPurple',
                width=12))
                             ), row=2, col=1)


    # make annotation at the value slighly shiftet in the
    fig.add_annotation(x=pH-1, y=DIC,
                       text="pH={:.2f} <br> DIC={:.6f} mol/l <br> DIC={:.6f} g/l <br> DIC= {:.6f} ppm".format(pH, DIC, DIC*M_C,DIC*M_C*1000),
                       showarrow=False,
                       yshift=1, row=2, col=1)

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
   
    fig.add_trace(go.Scatter(x=lines['pH'],y=lines['CO2_frac'],  mode='lines+markers',name=x_bar[3] ),row=3, col=1)
    fig.add_trace(go.Scatter(x=lines['pH'],y=lines['HCO3_frac'], mode='lines+markers',name=x_bar[1] ),row=3, col=1)
    fig.add_trace(go.Scatter(x=lines['pH'],y=lines['CO3_frac'], mode='lines+markers',name=x_bar[2]),row=3, col=1)

    
    
    fig.update_yaxes(title_text="Fraction in decimal ",title_standoff =4, ticksuffix='', row=3, col=1)
    
    fig.update_xaxes(title_text="pH", row=3, col=1)
    
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
            yshift=1,row=3, col=1)
    
    #get the concentrations of all the  species in the system
    # total


    cNa=sol.elements['Na']*1e+6

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




'''


if __name__ == '__main__':
    app.run_server(debug=True)

'''