# -*- coding: utf-8 -*-
"""
Dash multi‑page app for “Open Carbonate System Tools”.

Heavily re‑worked by Mert, and cleaned‑up.

how the wsgi file should look like:
https://community.plotly.com/t/dash-pythonanywhere-deployment-issue/5062

"""
import os, flask, pandas as pd, phreeqpython, plotly.graph_objects as go
from dash import Dash, html, dcc, dash_table, ctx 
from dash.dash_table import Format
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from numpy import log10
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────  CONSTANTS & STYLES  ──────────────────────────
MAX_WIDTH = "1160px"   # global content width (≈ 12‑col Bootstrap container)
PAD_Y     = "2rem"     # vertical padding for header / page bottom

# ─────────────────────────────  FLASK + DASH  ────────────────────────────────
server = flask.Flask(__name__)

BOOTSWATCH = "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/flatly/bootstrap.min.css"
HIGHLIGHT  = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/monokai-sublime.min.css"
HOVER_CSS = "https://cdnjs.cloudflare.com/ajax/libs/hover.css/2.3.1/css/hover-min.css"

app = Dash(
    __name__, server=server,
    external_stylesheets=[BOOTSWATCH, HIGHLIGHT, HOVER_CSS],
    external_scripts=[],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)

app.title = "Modeling Tools for Geochemistry"

# strip Dash's default footer
app.index_string = """<!DOCTYPE html><html lang=\"en\"><head>{%metas%}<title>{%title%}</title>{%favicon%}{%css%}</head><body>{%app_entry%}{%config%}{%scripts%}{%renderer%}</body></html>"""

# ─────────────────────────────  PATHS & HELPERS  ─────────────────────────────
BASE_DIR  = os.path.dirname(os.path.realpath(__file__))
ASSETS    = os.path.join(BASE_DIR, "assets")

def read_asset(fname: str) -> str:
    """Read UTF‑8 file from ./assets."""
    return open(os.path.join(ASSETS, fname), encoding="utf-8").read()

# Markdown / supporting text
NARRATIVE_MD  = read_asset("narrative_improved.md")
REFS_MD       = read_asset("references.md")
SOME_TEXT_MD  = read_asset("sometext.md")
INPUT_BOX_MD  = read_asset("Textbox_input.md")
OUTPUT_BOX_MD = read_asset("Textbox_output.md")

IMAGE_LOGO    = "/assets/uhh-logo-web.jpg"   # served by Dash `/assets` route

# ─────────────────────────────  SHARED UI COMPONENTS  ───────────────────────

def Footer() -> html.Footer:
    """Single footer placed by every top‑level layout, pinned to bottom."""
    link_style = {"margin": "0 .8rem", "color": "white", "textDecoration": "none"}
    return html.Footer(
        dbc.Container(
            [
                html.A("Impressum",       href="/impressum",        style=link_style),
                html.A("Datenschutz",     href="/datenschutz",     style=link_style),
                html.A("Barrierefreiheit",href="/barrierefreiheit", style=link_style),
            ],
            class_name="text-center",
            style={"maxWidth": MAX_WIDTH}
        ),
        style={
            "width": "100%",
            "backgroundColor": "#333",
            "color": "white",
            "padding": "12px 0",
            "marginTop": PAD_Y,
            "marginBottom": "0",       # no gap below footer
        },
    )

def SiteHeader(title: str, crumbs: list[tuple[str, str]] | None = None) -> html.Header:
    """Renders the header with logo, title and a breadcrumb that has no bottom margin."""
    # Build a manual breadcrumb so we can zero out the <ol> margin via mb-0
    if crumbs:
        # Create <li> items
        nav_items = []
        for lbl, href in crumbs[:-1]:
            nav_items.append(
                html.Li(html.A(lbl, href=href), className="breadcrumb-item")
            )
        # Last crumb is active text
        nav_items.append(
            html.Li(crumbs[-1][0],
                    className="breadcrumb-item active",
                    **{"aria-current": "page"})
        )
        # Wrap in <nav><ol class="breadcrumb mb-0 ps-0">...
        breadcrumb = html.Nav(
            html.Ol(nav_items,
                    className="breadcrumb mb-0 ps-0",
                    style={"marginBottom": "0"}),
            **{"aria-label": "breadcrumb"},
            className="mb-0"
        )
    else:
        breadcrumb = None

    return html.Header(
        dbc.Container(
            [
                html.Img(src=IMAGE_LOGO, style={"height": "90px"}),
                html.Div(
                    breadcrumb,
                    className="align-self-end"
                )
            ],
            class_name="d-flex align-items-center",
            style={
                "maxWidth": MAX_WIDTH,
                "paddingTop": PAD_Y,
                "paddingBottom": PAD_Y,
            },
        ),
        style={"borderBottom": "1px solid #ddd"},
    )


# ─────────────────────────────  LEGAL PAGES  ────────────────────────────────

# the three markdown files were converted from the original HTML
IMPRESSUM_MD    = read_asset("imprint.md")
DATENSCHUTZ_MD  = read_asset("datenschutz.md")
BARRECHT_MD     = read_asset("barrierefreiheit.md")

def legal_layout(raw_md: str, title: str, path: str) -> html.Div:
    return html.Div([
        SiteHeader(title, [("Home", "/"), (title, path)]),
        dbc.Container(dcc.Markdown(raw_md, className="pt-3"), style={"maxWidth": MAX_WIDTH}),
        Footer(),
    ])

# ──────────────────────────────────────────────────────────────────────────────
#  CALCULATOR
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
#  PHREEQP SET‑UP
# ──────────────────────────────────────────────────────────────────────────────
pp = phreeqpython.PhreeqPython(database="vitens.dat")

# ------------------------------------------------------------------
#  1)  CSV / look‑up tables
# ------------------------------------------------------------------
filepath = os.path.split(os.path.realpath(__file__))[0]

lines = pd.read_table(
    os.path.join(filepath, "assets/bjerrum_plot_update_phreeqpython.csv"),
    sep=",", keep_default_na=False, na_filter=False, engine="python"
)
DIC_line = pd.read_table(
    os.path.join(filepath, "assets/open_carbonate_system_phreeqpython.csv"),
    sep=",", keep_default_na=False, na_filter=False, engine="python"
)
elements = pd.read_csv(
    os.path.join(filepath, "assets/Periodic Table of Elements.csv"),
    sep=",", keep_default_na=False, na_filter=False, engine="python"
)
element_weights = dict(zip(elements["Symbol"], elements["AtomicMass"]))

# ------------------------------------------------------------------
#  2)  (Molar) constants
# ------------------------------------------------------------------
M_C     = 12.011
M_CH4   = 16.04
M_CO2   = 44.01
M_CO3   = 60.01
M_H     = 1.00784
M_H2    = M_H * 2
M_H2O   = 18.01528
M_HCO3  = 61.0168
M_Na    = 22.98976928
M_NaCO3 = M_CO3 + M_Na
M_NaHCO3= M_HCO3 + M_Na
M_OH    = 17.008
M_NaOH  = M_Na + M_OH
M_O     = 15.999
M_O2    = M_O * 2
M_Mg    = 24.305
M_Ca    = 40.078
M_K     = 39.0983
M_CaCO3 = M_Ca + M_C + 3 * M_O
M_MgCO3 = M_Mg + M_C + 3 * M_O
M_MgHCO3= M_Mg + M_HCO3
M_CaHCO3= M_Ca + M_HCO3
M_CaOH  = M_Ca + M_OH
M_MgOH  = M_Mg + M_OH

# ------------------------------------------------------------------
#  3)  conversion dict  (species → g per mol)
# ------------------------------------------------------------------
conv = {
    "CH4": M_CH4, "CO2": M_CO2, "CO3-2": M_CO3, "H+": M_H, "H2": M_H2,
    "H2O": M_H2O, "HCO3-": M_HCO3, "Na+": M_Na, "NaCO3-": M_NaCO3,
    "NaHCO3": M_NaHCO3, "NaOH": M_NaOH, "O2": M_O2, "OH-": M_OH,
    "Ca+2": M_Ca, "CaCO3": M_CaCO3, "Mg+2": M_Mg, "MgCO3": M_MgCO3,
    "MgHCO3+": M_MgHCO3, "MgOH+": M_MgOH, "CaHCO3+": M_CaHCO3,
    "CaOH+": M_CaOH, "K+": element_weights["K"], "Cl-": element_weights["Cl"],
    "H2S": 2 * element_weights["H"] + element_weights["S"],
    "HS-": element_weights["H"] + element_weights["S"],
    "HSO4-": element_weights["H"] + element_weights["S"] + 4 * element_weights["O"],
    "CaHSO4+": element_weights["Ca"] + element_weights["H"] + element_weights["S"] + 4 * element_weights["O"],
    "CaSO4": element_weights["Ca"] + element_weights["S"] + 4 * element_weights["O"],
    "KSO4-": element_weights["K"] + element_weights["S"] + 4 * element_weights["O"],
    "MgSO4": element_weights["Mg"] + element_weights["S"] + 4 * element_weights["O"],
    "NaSO4-": element_weights["Na"] + element_weights["S"] + 4 * element_weights["O"],
    "S-2": element_weights["S"], "SO4-2": element_weights["S"] + 4 * element_weights["O"],
    "N2": 2 * element_weights["N"], "NH3": element_weights["N"] + 3 * element_weights["H"],
    "NH4+": element_weights["N"] + 4 * element_weights["H"], "F-": element_weights["F"],
    "NH4SO4-": element_weights["N"] + 4 * element_weights["H"] + element_weights["S"] + 4 * element_weights["O"],
    "NO2-": element_weights["N"] + 2 * element_weights["O"],
    "NO3-": element_weights["N"] + 3 * element_weights["O"],
    "HF": element_weights["H"] + element_weights["F"],
    "HF2-": element_weights["H"] + 2 * element_weights["F"],
    "MgF+": element_weights["H"] + 2 * element_weights["F"],
    "NaF": element_weights["Na"] + element_weights["F"],
}

# ------------------------------------------------------------------
#  4)  strings for DataTable columns
# ------------------------------------------------------------------
TA_s     = "TAcarb [ueq/kgw]"
T_s      = "water T [degC]"
pCO2_s   = "air pCO2 [ppm]"

Na_s  = "Na⁺ [umol/kgw]"
Mg_s  = "Mg²⁺ [umol/kgw]"
Ca_s  = "Ca²⁺ [umol/kgw]"
K_s   = "K⁺ [umol/kgw]"
Cl_s  = "Cl- [umol/kgw]"
SO4_s = "SO₄²- [umol/kgw]"
NO2_s = "NO₃⁻ [umol/kgw]"
F_s   = "F- [umol/kgw]"
PO4_s = "PO₄³⁻ [umol/kgw]"

params   = [TA_s, T_s, pCO2_s]
cations  = [Na_s, Mg_s, Ca_s, K_s]
anions   = [Cl_s, SO4_s, NO2_s, F_s]

# ------------------------------------------------------------------
#  5)  small widgets used on the “Graph” view
# ------------------------------------------------------------------
T_range = [0, 80]
T_slider = dcc.Slider(
    id="T_input", min=T_range[0], max=T_range[1], step=0.5,
    marks={x: f"{x}°C" for x in range(T_range[0], T_range[1], 10)},
    value=20, tooltip={"placement": "bottom", "always_visible": True},
    updatemode="drag",
)
CO2_value = dcc.Input(id="CO2_input", type="number", value=415,
                      placeholder="Insert CO₂ (ppm)")
alkalinity_value = dcc.Input(id="TA_input", type="number", value=2500,
                             placeholder="Insert TA")
table_composition = "table_composition"

# ───────────────────────── helper ─────────────────────────
def make_table(
    df: pd.DataFrame,
    *, id: str,
    exponent: bool = False,          # ← True ⇒ 1.23 e‑04, False ⇒ 0.000123
) -> dash_table.DataTable:
    """Return a nicely‑styled DataTable."""
    num_fmt = Format.Format(
        precision=4,
        scheme=Format.Scheme.exponent if exponent else Format.Scheme.decimal,
        trim=True,
    )
    return dash_table.DataTable(
        id=id,
        columns=[{"name": c, "id": c, "type": "numeric", "format": num_fmt}
                 for c in df.columns],
        data=df.to_dict("records"),
        editable=True,

        style_table  = {"width": "100%", "overflowX": "auto",
                        "border": "1px solid #dee2e6", "margin": "0 auto"},
        style_header = {"backgroundColor": "#f8f9fa", "fontWeight": 600,
                        "padding": "10px"},
        style_cell   = {"padding": "8px 10px", "textAlign": "right",
                        "fontSize": "1rem", "minWidth": "80px"},
        style_data_conditional=[],
    )

# ─────────────────── build blank input tables ───────────────────
basic_tbl  = make_table(                       #  ← restore “sample”
    pd.DataFrame([dict(sample=1, **{p: 0 for p in params})]),
    id="table-bulk"
)
cation_tbl = make_table(
    pd.DataFrame([dict(sample=1, **{p: 0 for p in cations})]),
    id="table-cations"
)
anion_tbl  = make_table(
    pd.DataFrame([dict(sample=1, **{p: 0 for p in anions})]),
    id="table-anions"
)

# highlight zeros in red
for tbl, cols in [(basic_tbl, params), (cation_tbl, cations), (anion_tbl, anions)]:
    tbl.style_data_conditional += [
        {"if": {"filter_query": f"{{{c}}} = 0", "column_id": c},
         "backgroundColor": "#ffe5e5", "color": "black"} for c in cols
    ]

# cards
basic_card  = dbc.Card(
    [dbc.CardHeader("Basic parameters", class_name="fw-bold"),
     dbc.CardBody(basic_tbl)], class_name="mb-4 shadow-sm")
cation_card = dbc.Card(
    [dbc.CardHeader("Cations", class_name="fw-bold"),
     dbc.CardBody(cation_tbl)], class_name="mb-4 shadow-sm")
anion_card  = dbc.Card(
    [dbc.CardHeader("Anions", class_name="fw-bold"),
     dbc.CardBody(anion_tbl)], class_name="mb-4 shadow-sm")

# ─────────────────── TABLE‑view layout ───────────────────
page1_layout = html.Div(
    [
        dbc.Container(
            [
                dcc.Markdown(NARRATIVE_MD, mathjax=True),

                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button("Table", id="btn-page-1", n_clicks=0,
                                       color="success", className="w-100",
                                       style={"fontSize": "1.3em",
                                              "backgroundColor": "#149c7d",
                                              "pointerEvents": "none"})),
                        dbc.Col(
                            dbc.Button("Graph", id="btn-page-2", n_clicks=0,
                                       color="success", className="w-100",
                                       style={"fontSize": "1.3em"})),
                    ],
                    class_name="my-4",
                ),

                # ---------------- INPUT ----------------
                html.H2("Input tables"),
                dcc.Markdown(INPUT_BOX_MD, mathjax=True),
                basic_card,
                cation_card,
                anion_card,

                # ---------------- OUTPUT ----------------
                html.H2("Output tables"),
                html.B("Resulting speciation after equilibration:"),
                html.Div(id="table1", className="my-3"),
                html.B("Saturation indices of possible minerals:"),
                html.Plaintext("Oversaturated minerals are highlighted red."),
                html.Div(id="table2", className="my-3"),
                html.B("Bulk parameters:"),
                html.Div(id="table3", className="my-3"),

                dcc.Markdown(SOME_TEXT_MD, mathjax=True, className="mt-4"),
                dcc.Markdown(REFS_MD,        mathjax=True, className="mt-4"),
            ],
            fluid=True,     # full‑width container
        ),
    ],
    style={"fontSize": "1.15em",
           "maxWidth": MAX_WIDTH,             # centre whole page
           "margin": "0 auto"},
)

# ───────────────────────────── page‑2  (GRAPH view) ─────────────────────────
page2_layout = html.Div(
    [
        dbc.Container(
            [
                dcc.Markdown(NARRATIVE_MD, mathjax=True),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button("Table", id="btn-page-1", n_clicks=0,
                                       color="success", className="w-100",
                                       style={"fontSize": "1.5em"}),
                        ),
                        dbc.Col(
                            dbc.Button("Graph", id="btn-page-2", n_clicks=0,
                                       color="success", className="w-100",
                                       style={"fontSize": "1.5em",
                                              "backgroundColor": "#149c7d",
                                              "pointerEvents": "none"}),
                        ),
                    ],
                    class_name="my-4",
                ),
                dbc.Row([dbc.Col("Water temperature [°C] :", md=4),
                         dbc.Col(T_slider, md=8)]),
                dbc.Row([dbc.Col("CO₂ partial pressure [ppm] :", md=4),
                         dbc.Col(CO2_value, md=8)], className="mt-2"),
                dbc.Row([dbc.Col("Total alkalinity [ueq/L] :", md=4),
                         dbc.Col(alkalinity_value, md=8)], className="mt-2"),
                dcc.Graph(id="indicator-graphic", style={"height": "150vh"}),
                html.B("Resulting speciation after the water equilibrates with the atmosphere:"),
                html.Div(id=table_composition, className="my-3"),
                dcc.Markdown(SOME_TEXT_MD, mathjax=True, className="mt-4"),
                dcc.Markdown(REFS_MD,      mathjax=True, className="mt-4"),
            ],
            fluid=True,
        )
    ],
    style={"fontSize": "1.15em",
           "maxWidth": MAX_WIDTH,             # centre whole page
           "margin": "0 auto"},
)
# ------------------------------------------------------------------
#  8)  MAIN CALLBACKS  (unchanged)
#      • update_graph      – handles TABLE view output tables
#      • update_graph_2    – produces GRAPH view figure + table
# ------------------------------------------------------------------
@app.callback(
    [Output("table1", "children"),
     Output("table2", "children"),
     Output("table3", "children")],
    [Input("table-bulk",    "data"),   Input("table-bulk",    "columns"),
     Input("table-cations", "data"),   Input("table-cations", "columns"),
     Input("table-anions",  "data"),   Input("table-anions",  "columns")]
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

        tbl1 = make_table(df,        id="table1-dt", exponent=True)   # scientific
        #output the saturation index table

        df_phases=pd.DataFrame.from_dict(sol.phases, orient='index', columns=['saturation index (SI)'])

        df_phases = df_phases.rename_axis(['mineral']).reset_index()

        df_phases['IAP/Ksp']=10**df_phases['saturation index (SI)']
        # get SI of the phases


        tbl2 = make_table(df_phases, id="table2-dt", exponent=True)   # scientific

        tbl2.style_data_conditional.extend([   # keep SI highlighting
            {"if": {"filter_query": "{saturation index (SI)} > 0",
                    "column_id": "saturation index (SI)"}, "backgroundColor": "tomato", "color": "white"},
            {"if": {"filter_query": "{IAP/Ksp} > 1",
                    "column_id": "IAP/Ksp"},               "backgroundColor": "tomato", "color": "white"},
        ])

        #
        #

        # calculate DIC

        d={'Dissolved inorganic carbon [mol/kgw]':[DIC],'pH':[pH],'EC [uS/cm]':[SC]}

        df_extra=pd.DataFrame.from_dict(d,orient='index',columns=['number'])

        df_extra = df_extra.rename_axis(['variable']).reset_index()


        tbl3 = make_table(df_extra,  id="table3-dt", exponent=False)  # plain

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
# ─────────────────────────────────────────────────────────────────────────────

# ----------------------  WRAPPER for Calculator  ---------------------------

def calc_layout() -> html.Div:
    return html.Div([
        SiteHeader("Alkalinity Tool", [("Home", "/"), ("Alkalinity Tool", "/carbonate-system-modeling")]),
        html.Div(id="subpage-content", children=page1_layout),
        Footer(),
    ])

# toggle Table / Graph sub‑pages
@app.callback(Output("subpage-content", "children"),
              Input("btn-page-1", "n_clicks"), Input("btn-page-2", "n_clicks"))
def _toggle_pages(n1, n2):
    return page2_layout if ctx.triggered_id == "btn-page-2" else page1_layout

# ─────────────────────────────  APP LAYOUT WRAP ─────────────────────────────
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id="page-layout", style={"flex": "1 0 auto"}),
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "minHeight": "100vh",    # ensure full viewport
        "margin": "0",
    },
)


# ───────────────────────────────  HOME PAGE ────────────────────────────────
def home_layout() -> html.Div:
    # Hero + cards in one section
    hero = html.Div(
        [
            html.H1(
                "Modeling Tools for Geochemistry",
                className="display-3 fw-bold text-white",
            ),
            html.P(
                "Interactive calculators for carbonate chemistry and XRF data—built for students, researchers, and practitioners.",
                className="lead text-white mx-auto",
                style={"maxWidth": "700px"},
            ),
            # cards row inside the hero
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Open Carbonate System Water Speciation", className="card-title fw-semibold"),
                                    html.P(
                                        "Compute open‑system carbonate speciation in fresh waters with both table and graph views.",
                                        className="card-text",
                                    ),
                                    dbc.Button(
                                        "Launch Alkalinity Tool",
                                        color="light",
                                        href="/carbonate-system-modeling",
                                    ),
                                ],
                                className="d-flex flex-column justify-content-between h-100",
                            ),
                            className="h-100 border-0 hvr-shadow",
                            style={"borderRadius": "1rem", "padding": "1.5rem"},
                        ),
                        md=6, lg=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("XRF data simulator", className="card-title fw-semibold"),
                                    html.P(
                                        "This tool calculates theoretical oxide weight percentages from a mineral’s plain chemical formula. By parsing the formula, it derives the idealized composition of the pure mineral,"
                                        " including contributions from common oxides. The results are useful for XRF normalization, geochemical modeling, and educational purposes.",
                                        className="card-text",
                                    ),
                                    dbc.Button("Coming Soon", color="secondary", disabled=True),
                                ],
                                className="d-flex flex-column justify-content-between h-100",
                            ),
                            className="h-100 border-0 hvr-shadow",
                            style={"borderRadius": "1rem", "padding": "1.5rem"},
                        ),
                        md=6, lg=4,
                    ),
                ],
                className="g-4 justify-content-center mt-4",
            ),
        ],
        className="text-center py-5 px-3",
        style={"backgroundColor": "#149c7d"},
    )

    return html.Div(
        [
            SiteHeader("Startseite"),
            hero,
            # push footer down
            html.Div(style={"flex": "1 0 auto"}),
            Footer(),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "minHeight": "100vh",
            "margin": "0",
        },
    )


# ────────────────────────  PAGE ROUTING CALLBACK ─────────────────────────
@app.callback(Output("page-layout", "children"), Input("url", "pathname"))
def display_page(pathname: str):
    if pathname in ("/", ""):
        return home_layout()
    if pathname == "/carbonate-system-modeling":
        return calc_layout()
    if pathname == "/impressum":
        return legal_layout(IMPRESSUM_MD, "Impressum", pathname)
    if pathname == "/datenschutz":
        return legal_layout(DATENSCHUTZ_MD, "Datenschutz", pathname)
    if pathname == "/barrierefreiheit":
        return legal_layout(BARRECHT_MD, "Barrierefreiheit", pathname)

    # 404 fallback
    return html.Div(
        [
            SiteHeader("404 – Seite nicht gefunden", [("Home", "/")]),
            dbc.Container(html.H3("Die angeforderte Seite existiert nicht."), style={"maxWidth": MAX_WIDTH}),
            Footer(),
        ],
        style={"display": "flex", "flexDirection": "column", "flex": "1 0 auto"},
    )

# ─────────────────────────────  DEV ENTRY‑POINT  ────────────────────────────
if __name__ == "__main__":
    app.run(debug=False)
