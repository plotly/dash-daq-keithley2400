# In[]:
# Import required libraries
import numpy as np

import plotly.graph_objs as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event

import dash_daq as daq

app = dash.Dash('')

server = app.server

external_css = ["https://codepen.io/bachibouzouk/pen/ZRjdZN.css"]

for css in external_css:

    app.css.append_css({"external_url": css})

app.config.suppress_callback_exceptions = False

app.scripts.config.serve_locally = True

# line colors
line_colors = ['#19d3f3', '#e763fa', '#00cc96', '#EF553B']


class UsefulVariables():
    def __init__(self):
        self.n_clicks = 0
        self.n_refresh = 0
        self.sourced_values = []
        self.measured_values = []

    def change_n_clicks(self, nclicks):
        print('\nchanged n_clicks in the local vars \n')
        self.n_clicks = nclicks

    def reset_n_clicks(self):
        self.n_clicks = 0

    def change_n_refresh(self, nrefresh):
        self.n_refresh = nrefresh

    def reset_interval(self):
        self.n_refresh = 0


local_vars = UsefulVariables()


def function_hdr(func):
    def new_function(*args, **kwargs):
        print("\n### %s ###\n" % (func.__name__))
        return_value = func(*args, **kwargs)
        print("\n### %s ###\n" % ('-' * len(func.__name__)))
        return return_value

    return new_function


def fake_iv_relation(v, c1=1, c2=1, v_0c=10, i_sc=1):
    """mimic an IV curve
    source: https://www.sciencedirect.com/science/article/pii/S1658365512600120
    """
    if v < v_0c and v > 0:
        # return i_sc*(1-c1*np.exp(v/(c2*v_0c)-1))
        return np.round(np.sqrt(v_0c)-np.sqrt(v), 4)
    else:
        return 0


# to pick the first theme between dark and light
MY_THEME = 'light'

# font and background colors associated with each themes
bkg_color = {'dark': '#2a3f5f', 'light': '#F3F6FA'}
grid_color = {'dark': 'white', 'light': '#C8D4E3'}
text_color = {'dark': 'white', 'light': '#506784'}


def get_source_labels(source='V'):
    """labels for source/measure elements"""

    if source == 'V':
        # we source voltage and measure current
        source_label = 'Voltage'
        measure_label = 'Current'
    else:
        # we source current and measure voltage
        source_label = 'Current'
        measure_label = 'Voltage'

    return source_label, measure_label


def get_source_units(source='V'):
    """unitss for source/measure elements"""

    if source == 'V':
        # we source voltage and measure current
        source_unit = 'V'
        measure_unit = 'A'
    else:
        # we source current and measure voltage
        source_unit = 'A'
        measure_unit = 'V'

    return source_unit, measure_unit


h_style = {
    'display': 'flex',
    'flex-direction': 'row',
    'alignItems': 'center',
    'justifyContent': 'space-between',
    'margin': '5px'
}


# Create controls using a function
@function_hdr
def generate_main_layout(
    theme='light',
    src_type='V',
    mode_val='single',
    fig=None,
):
    """generate the layout of the app"""

    source_label, measure_label = get_source_labels(src_type)
    source_unit, measure_unit = get_source_units(src_type)

    if mode_val == 'single':
        single_style = {
            'display': 'flex',
            'flex-direction': 'column',
            'alignItems': 'center'
        }
        sweep_style = {'display': 'none'}

        label_btn = 'Single measure'
    else:
        single_style = {'display': 'none'}
        sweep_style = {
            'display': 'flex',
            'flex-direction': 'column',
            'alignItems': 'center'
        }

        label_btn = 'Start sweep'

    # As the trigger-measure btn will have its n_clicks reset by the reloading
    # of the layout we need to reset this one as well
    local_vars.reset_n_clicks()

    # Doesn't clear the data of the graph
    if fig is None:
        data = []
    else:
        data = fig['data']

    html_layout = [
        html.Div(
            className='row',
            children=[
                # graph to trace out the result(s) of the measurement(s)
                html.Div(
                    className="eight columns",
                    children=[
                        dcc.Graph(
                            id='IV_graph',
                            figure={
                                'data': data,
                                'layout': dict(
                                    paper_bgcolor=bkg_color[theme],
                                    plot_bgcolor=bkg_color[theme],
                                    font=dict(
                                        color=text_color[theme],
                                        size=15,
                                    ),
                                    xaxis={
                                        'color': grid_color[theme],
                                        'gridcolor': grid_color[theme]
                                    },
                                    yaxis={
                                        'color': grid_color[theme],
                                        'gridcolor': grid_color[theme]
                                    }
                                )
                            }
                        )
                    ]
                ),
                # controls and options for the IV tracer
                html.Div(
                    className="two columns",
                    id='IV-options',
                    children=[
                        html.H4(
                            'Sourcing :',
                            title='Choose whether you want to source voltage '
                                  'and measure current or source current and '
                                  'measure voltage'
                        ),
                        dcc.RadioItems(
                            id='source-choice',
                            options=[
                                {'label': 'Voltage', 'value': 'V'},
                                {'label': 'Current', 'value': 'I'}
                            ],
                            value=src_type
                        ),
                        html.Br(),
                        html.H4(
                            'Measure mode :',
                            title='Choose if you want to do single measurement'
                                  ' or to start a sweep'
                        ),
                        dcc.RadioItems(
                            id='mode-choice',
                            options=[
                                {'label': 'Single measure', 'value': 'single'},
                                {'label': 'Sweep', 'value': 'sweep'}
                            ],
                            value=mode_val
                        ),
                        html.Br(),
                        daq.PowerButton(
                            on=True
                        )
                    ]
                )
            ]
        ),
        html.Div(
            id='measure_controls',
            className='row',
            children=[
                # Sourcing controls
                html.Div(
                    id='source-div',
                    className="three columns",
                    children=[
                        # To perform single measures adjusting the source with
                        # a knob
                        html.Div(
                            id='single_div',
                            children=[
                                daq.Knob(
                                    id='source-knob',
                                    value=0.0,
                                    label='%s (%s)' % (
                                        source_label,
                                        source_unit
                                    )
                                ),
                                daq.LEDDisplay(
                                    id="source-knob-display",
                                    label='Knob readout',
                                    value="0.0000"
                                )
                            ],
                            style=single_style
                        ),
                        # To perfom automatic sweeps of the source
                        html.Div(
                            id='sweep_div',
                            children=[
                                html.Div(
                                    id='sweep-title',
                                    children=html.H4(
                                        "%s sweep:" % source_label
                                    )
                                ),
                                html.Div(
                                    [
                                        'Start',
                                        html.Br(),
                                        daq.PrecisionInput(
                                            id='sweep-start',
                                            precision=4,
                                            label=' %s' % source_unit,
                                            labelPosition='right',
                                            value=1
                                        )
                                    ],
                                    title='The lowest value of the sweep',
                                    style=h_style
                                ),
                                html.Div(
                                    [
                                        'Stop',
                                        daq.PrecisionInput(
                                            id='sweep-stop',
                                            precision=4,
                                            label=' %s' % source_unit,
                                            labelPosition='right',
                                            value=9
                                        )
                                    ],
                                    title='The highest value of the sweep',
                                    style=h_style
                                ),
                                html.Div(
                                    [
                                        'Step',
                                        daq.PrecisionInput(
                                            id='sweep-step',
                                            precision=4,
                                            label=' %s' % source_unit,
                                            labelPosition='right',
                                            value=1
                                        )
                                    ],
                                    title='The increment of the sweep',
                                    style=h_style
                                ),
                                html.Div(
                                    [
                                        'Time of a step',
                                        daq.NumericInput(
                                            id='sweep-dt',
                                            value=0.5
                                        ),
                                        's'
                                    ],
                                    title='The time spent on each increment',
                                    style=h_style
                                ),
                                html.Div(
                                    [
                                        daq.Indicator(
                                            id='sweep-status',
                                            label='Sweep active',
                                            value=False
                                        )
                                    ],
                                    title='Indicates if the sweep is running',
                                    style=h_style
                                )
                            ],
                            style=sweep_style
                        )
                    ]
                ),
                # measure button and indicator
                html.Div(
                    id='trigger-div',
                    className="two columns",
                    children=[
                        daq.StopButton(
                            id='trigger-measure',
                            buttonText=label_btn,
                            size=150
                        ),
                        daq.Indicator(
                            id='measure-triggered',
                            value=False,
                            label='Measure active'
                            #style={'display': 'none'}
                        ),
                    ]
                ),
                # Display the sourced and measured values
                html.Div(
                    id='measure-div',
                    className="five columns",
                    children=[
                        daq.LEDDisplay(
                            id="source-display",
                            label='Applied %s (%s)' % (
                                source_label,
                                source_unit
                            ),
                            value="0.0000"
                        ),
                        daq.LEDDisplay(
                            id="measure-display",
                            label='Measured %s (%s)' % (
                                measure_label,
                                measure_unit
                            ),
                            value="0.0000"
                        )
                    ]
                )

            ],
            style={
                'width': '100%',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'space-between'
            }
        ),
        html.Div(
            className='row',
            children=[
                html.Div(
                    id='',
                    className="five columns",
                    children=[
                        html.H5('Here the voltage')
                    ]
                ),
                html.Div(
                    id='graph_controls',
                    className="five columns",
                    children=[
                        html.H5('Here the current')
                    ]
                )
            ]
        ),
        html.Div(
            className='row',
            children=[
                html.Div(
                    className='ten columns',
                    children=dcc.Markdown('''
**What is this app about?**

This is an app to show the graphic elements of Dash DAQ used to create an
interface for the voltage/current source/measure from Keithley 2400. This mock
demo does not actually connect to a physical instrument the values diplayed are
generated randomly for demonstration purposes.

**How to use the app**

DESCRIBE HOW TO USE THE APP HERE You can purchase the Dash DAQ components at [
dashdaq.io](https://www.dashdaq.io/)
                    '''),
                    style={
                        # 'max-width': '600px',
                        'margin': '15px auto 300 px auto',
                        'padding': '40px',
                        'alignItems': 'center',
                        'box-shadow': '10px 10px 5px rgba(0, 0, 0, 0.2)',
                        'border': '1px solid #DFE8F3',
                        'color': text_color[theme],
                        'background': bkg_color[theme]
                    }
                )
            ]
        )
    ]

    if theme == 'dark':
        return daq.DarkThemeProvider(children=html_layout)
    elif theme == 'light':
        return html_layout


root_layout = html.Div(
    id='main_page',
    children=[
        dcc.Location(id='url', refresh=False),
        dcc.Interval(id='refresher', interval=1000000),
        html.Div(
            id='header',
            className='banner',
            children=[
                html.H2('Dash DAQ: IV curve tracer'),
                daq.ToggleSwitch(
                    id='toggleTheme',
                    label='Dark/Light layout',
                    size=30,
                ),
                html.Img(
                    src='https://s3-us-west-1.amazonaws.com/plotly'
                        '-tutorials/excel/dash-daq/dash-daq-logo'
                        '-by-plotly-stripe.png',
                    style={
                        'height': '100',
                        'float': 'right',
                    }
                )
            ],
            style={
                'width': '100%',
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'background': '#A2B1C6',
                'color': '#506784'
            }
        ),
        html.Div(
            id='page-content',
            children=generate_main_layout(theme=MY_THEME),
            # className='ten columns',
            style={
                'width': '100%'
            }
        )
    ]
)


# In[]:
# Create app layout
app.layout = root_layout


# In[]:
# Create callbacks
# ======= Dark/light themes callbacks =======
@app.callback(
    Output('page-content', 'children'),
    [
        Input('toggleTheme', 'value')
    ],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value'),
        State('IV_graph', 'figure')
    ]
)
def page_layout(value, src_type, mode_val, fig):
    """update the theme of the daq components"""

    if value:
        return generate_main_layout('dark', src_type, mode_val, fig)
    else:
        return generate_main_layout('light', src_type, mode_val, fig)


@app.callback(
    Output('page-content', 'style'),
    [Input('toggleTheme', 'value')],
    [State('page-content', 'style')]
)
def page_style(value, style_dict):
    """update the theme of the app"""
    if value:
        theme = 'dark'
    else:
        theme = 'light'

    style_dict['color'] = text_color[theme]
    style_dict['background'] = bkg_color[theme]
    return style_dict


# ======= Callbacks for changing labels =======
@app.callback(
    Output('source-knob', 'label'),
    [],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('source-choice', 'change'),
        Event('mode-choice', 'change')
    ]
)
def source_knob_label(src_type, mode_val):
    """update label upon modification of Radio Items"""
    source_label, measure_label = get_source_labels(src_type)
    return source_label


@app.callback(
    Output('source-knob-display', 'label'),
    [],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('source-choice', 'change'),
        Event('mode-choice', 'change')
    ]
)
def source_knob_display_label(scr_type, mode_val):
    """update label upon modification of Radio Items"""
    source_label, measure_label = get_source_labels(scr_type)
    source_unit, measure_unit = get_source_units(scr_type)
    return 'Value : %s (%s)' % (source_label, source_unit)


@app.callback(
    Output('sweep-start', 'label'),
    [],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('source-choice', 'change'),
        Event('mode-choice', 'change')
    ]
)
def sweep_start_label(src_type, mode_val):
    """update label upon modification of Radio Items"""
    source_unit, measure_unit = get_source_units(src_type)
    return source_unit


@app.callback(
    Output('sweep-stop', 'label'),
    [],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('source-choice', 'change'),
        Event('mode-choice', 'change')
    ]
)
def sweep_stop_label(src_type, mode_val):
    """update label upon modification of Radio Items"""
    source_unit, measure_unit = get_source_units(src_type)
    return source_unit


@app.callback(
    Output('sweep-step', 'label'),
    [],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('source-choice', 'change'),
        Event('mode-choice', 'change')
    ]
)
def sweep_step_label(src_type, mode_val):
    """update label upon modification of Radio Items"""
    source_unit, measure_unit = get_source_units(src_type)
    return source_unit


@app.callback(
    Output('sweep-title', 'children'),
    [],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('source-choice', 'change'),
        Event('mode-choice', 'change')
    ]
)
def sweep_title_label(src_type, mode_val):
    """update label upon modification of Radio Items"""
    source_label, measure_label = get_source_labels(src_type)
    return html.H4("%s sweep:" % source_label)


@app.callback(
    Output('source-display', 'label'),
    [],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('source-choice', 'change'),
        Event('mode-choice', 'change')
    ]
)
def source_display_label(src_type, mode_val):
    """update label upon modification of Radio Items"""
    source_label, measure_label = get_source_labels(src_type)
    source_unit, measure_unit = get_source_units(src_type)
    return 'Applied %s (%s)' % (source_label, source_unit)


@app.callback(
    Output('measure-display', 'label'),
    [],
    [
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('source-choice', 'change'),
        Event('mode-choice', 'change')
    ]
)
def measure_display_label(src_type, mode_val):
    """update label upon modification of Radio Items"""
    source_label, measure_label = get_source_labels(src_type)
    source_unit, measure_unit = get_source_units(src_type)
    return 'Measured %s (%s)' % (measure_label, measure_unit)


@app.callback(
    Output('trigger-measure', 'buttonText'),
    [],
    [
        State('mode-choice', 'value')
    ],
    [
        Event('mode-choice', 'change')
    ]
)
def trigger_measure_label(mode_val):
    """update the measure button upon choosing single or sweep"""
    if mode_val == 'single':
        return 'Single measure'
    else:
        return 'Start sweep'


# ======= Callbacks to change elements in the layout =======
@app.callback(
    Output('single_div', 'style'),
    [],
    [
        State('mode-choice', 'value')
    ],
    [
        Event('mode-choice', 'change')
    ]
)
def single_div_toggle_style(mode_val):
    """toggle the layout for single measure"""
    if mode_val == 'single':
        return {
            'display': 'flex',
            'flex-direction': 'column',
            'alignItems': 'center'
        }
    else:
        return {'display': 'none'}


@app.callback(
    Output('sweep_div', 'style'),
    [],
    [
        State('mode-choice', 'value')
    ],
    [
        Event('mode-choice', 'change')
    ]
)
def sweep_div_toggle_style(mode_val):
    """toggle the layout for sweep"""
    if mode_val == 'single':
        return {'display': 'none'}
    else:
        return {
            'display': 'flex',
            'flex-direction': 'column',
            'alignItems': 'center'
        }


# ======= Applied/measured values display =======
@app.callback(
    Output('source-knob', 'value'),
    [],
    [],
    [
        Event('source-choice', 'change')
    ]
)
def knob_reset():
    """reset the display to 0 when the source is toggled"""
    return '0'


# ======= Interval callbacks =======
@app.callback(
    Output('refresher', 'interval'),
    [
        Input('sweep-status', 'value')
    ],
    [
        State('mode-choice', 'value'),
        State('sweep-dt','value')
    ]
)
def interval_toggle(swp_on, mode_val, dt):
    """change the interval to high frequency for sweep"""
    if mode_val == 'single':
        return 1000000
    else:
        if swp_on:
            return dt * 1000
        else:
            return 1000000


@app.callback(
    Output('refresher', 'n_intervals'),
    [],
    [
        State('sweep-status', 'value'),
        State('mode-choice', 'value'),
        State('refresher', 'n_intervals')
    ],
    [
        Event('mode-choice', 'change'),
        Event('trigger-measure', 'click')
    ]
)
def reset_interval(swp_on, mode_val, n_interval):
    """reset the n_interval of the dcc.Interval once a sweep is done"""
    if mode_val == 'single':
        local_vars.reset_interval()
        return 0
    else:
        if swp_on:
            return n_interval
        else:
            local_vars.reset_interval()
            return 0


@app.callback(
    Output('sweep-status', 'value'),
    [
        Input('source-display', 'value')
    ],
    [
        State('measure-triggered', 'value'),
        State('sweep-status', 'value'),
        State('sweep-stop', 'value'),
        State('sweep-step', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('trigger-measure', 'click')
    ]
)
def sweep_activation_toggle(
    sourced_val,
    meas_triggered,
    swp_on,
    swp_stop,
    swp_step,
    mode_val
):
    """decide whether to turn on or off the sweep
    when single mode is selected, it is off by default
    when sweep mode is selected, it enables the sweep if is wasn't on
    otherwise it stops the sweep once the sourced value gets higher or equal
    than the sweep limit minus the sweep step
    """
    if mode_val == 'single':
        return False
    else:
        if swp_on:
            # The condition of continuation is to source lower than the sweep
            # limit minus one sweep step
            answer = float(sourced_val) <= float(swp_stop)-float(swp_step)
            return answer
        else:
            if not meas_triggered:
                # The 'trigger-measure' wasn't pressed yet
                return False
            else:
                # Initiate a sweep
                return True


# ======= Measurements callbacks =======
@app.callback(
    Output('source-knob-display', 'value'),
    [
        Input('source-knob', 'value')
    ]
)
def set_source_knob_display(knob_val):
    """"set the value of the knob on a LED display"""
    return knob_val


@app.callback(
    Output('measure-triggered', 'value'),
    [
        Input('trigger-measure', 'n_clicks'),
    ],
    [
        State('mode-choice', 'value'),
        State('sweep-status', 'value')
    ],
)
def update_trigger_measure(
    nclick,
    mode_val,
    swp_on
):
    """ Controls if a measure can be made or not
    The indicator 'measure-triggered' can be set to True only by a click
    on the 'trigger-measure' button or by the 'refresher' interval
    """

    if nclick is None:
        nclick = 0

    if int(nclick) != local_vars.n_clicks:
        # It was triggered by a click on the trigger-measure button
        local_vars.change_n_clicks(int(nclick))
        return True
    else:
        return False


@app.callback(
    Output('source-display', 'value'),
    [
        Input('refresher', 'n_intervals'),
        Input('measure-triggered', 'value'),
    ],
    [
        State('source-knob', 'value'),
        State('source-display', 'value'),
        State('sweep-start', 'value'),
        State('sweep-stop', 'value'),
        State('sweep-step', 'value'),
        State('source-choice', 'value'),
        State('mode-choice', 'value'),
        State('sweep-status', 'value')
    ]
)
def set_source_display(
    n_interval,
    meas_triggered,
    knob_val,
    old_source_display_val,
    swp_start,
    swp_stop,
    swp_step,
    src_type,
    mode_val,
    swp_on
):
    """"set the source value to the instrument"""

    if mode_val == 'single':
        return knob_val
    else:
        if meas_triggered:
            if swp_on:
                answer = float(swp_start) \
                         + (int(n_interval) - 1) * float(swp_step)
                if answer > float(swp_stop):
                    return old_source_display_val
                else:
                    return answer
            else:
                return old_source_display_val
        else:
            return old_source_display_val


@app.callback(
    Output('measure-display', 'value'),
    [
        Input('source-display', 'value')
    ],
    [
        State('measure-triggered', 'value'),
        State('measure-display', 'value'),
        State('source-choice', 'value'),
        State('mode-choice', 'value'),
        State('sweep-status', 'value')
    ]
)
def update_measure_display(
    src_val,
    meas_triggered,
    meas_old_val,
    src_type,
    mode_val,
    swp_on
):
    """"read the measured value from the instrument"""
    # check that the applied value correspond to source-knob
    # initiate a measure of the KT2400
    # read the measure value and return it
    if mode_val == 'single':
        if meas_triggered:
            source_value = float(src_val)

            local_vars.sourced_values.append(source_value)

            measured_value = fake_iv_relation(source_value)
            local_vars.measured_values.append(measured_value)

            return measured_value
        else:
            return meas_old_val

    else:
        if meas_triggered:

            if swp_on:
                source_value = float(src_val)
                local_vars.sourced_values.append(source_value)

                measured_value = fake_iv_relation(source_value)
                local_vars.measured_values.append(measured_value)

                return measured_value
            else:
                return meas_old_val
        else:
            return meas_old_val


@app.callback(
    Output('IV_graph', 'figure'),
    [
        Input('toggleTheme', 'value'),
        Input('measure-display', 'value')
    ],
    [
        State('measure-triggered', 'value'),
        State('source-display', 'value'),
        State('IV_graph', 'figure'),
        State('source-choice', 'value'),
        State('mode-choice', 'value'),
        State('sweep-status', 'value')
    ]
)
def update_graph(
        theme,
        measured_val,
        meas_triggered,
        sourced_val,
        graph_data,
        src_type,
        mode_val,
        swp_on
):
    """"update the IV graph"""
    if theme:
        theme = 'dark'
    else:
        theme = 'light'

    print("graph triggered")
    print(sourced_val)
    print(measured_val)
    print(meas_triggered)
    print(swp_on)
    # Labels for sourced and measured quantities
    source_label, measure_label = get_source_labels(src_type)
    source_unit, measure_unit = get_source_units(src_type)

    if mode_val == 'single':
        if meas_triggered:
            # The change to the graph was triggered by a measure

            # Sort the data so the are ascending in x
            data_array = np.vstack(
                [
                    local_vars.sourced_values,
                    local_vars.measured_values
                ]
            )
            data_array = data_array[:, data_array[0, :].argsort()]

            xdata = data_array[0, :]
            ydata = data_array[1, :]

            data_for_graph = [
                go.Scatter(
                    x=xdata,
                    y=ydata,
                    mode='lines+markers',
                    name='IV curve',
                    line={
                        'color': '#EF553B',
                        'width': 2
                    }
                )
            ]

            return {
                'data': data_for_graph,
                'layout': dict(
                    xaxis={
                        'title': 'Applied %s (%s)' % (
                            source_label, source_unit
                        ),
                        'color': text_color[theme],
                        'gridcolor': grid_color[theme]
                    },
                    yaxis={
                        'title': 'Measured %s (%s)' % (
                            measure_label,
                            measure_unit
                        ),
                        'gridcolor': grid_color[theme]
                    },
                    font=dict(
                        color=text_color[theme],
                        size=15,
                    ),
                    margin={'l': 100, 'b': 100, 't': 50, 'r': 20, 'pad': 0},
                    plot_bgcolor=bkg_color[theme],
                    paper_bgcolor=bkg_color[theme]
                )
            }
        else:
            return graph_data
    else:
        if swp_on:
            # The change to the graph was triggered by a measure

            # Sort the data so the are ascending in x
            data_array = np.vstack(
                [
                    local_vars.sourced_values,
                    local_vars.measured_values
                ]
            )
            data_array = data_array[:, data_array[0, :].argsort()]

            xdata = data_array[0, :]
            ydata = data_array[1, :]

            data_for_graph = [
                go.Scatter(
                    x=xdata,
                    y=ydata,
                    mode='lines+markers',
                    name='IV curve',
                    line={
                        'color': '#EF553B',
                        'width': 2
                    }
                )
            ]

            return {
                'data': data_for_graph,
                'layout': dict(
                    xaxis={
                        'title': 'Applied %s (%s)' % (
                            source_label, source_unit
                        ),
                        'color': text_color[theme],
                        'gridcolor': grid_color[theme]
                    },
                    yaxis={
                        'title': 'Measured %s (%s)' % (
                            measure_label,
                            measure_unit
                        ),
                        'gridcolor': grid_color[theme]
                    },
                    font=dict(
                        color=text_color[theme],
                        size=15,
                    ),
                    margin={'l': 100, 'b': 100, 't': 50, 'r': 20, 'pad': 0},
                    plot_bgcolor=bkg_color[theme],
                    paper_bgcolor=bkg_color[theme]
                )
            }
        else:
            return graph_data


# In[]:
# Main
if __name__ == '__main__':
    app.run_server(debug=True)
