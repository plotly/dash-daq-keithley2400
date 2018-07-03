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


def generate_source_mode_layout(source='V', mode='single'):
    """"generate the layout of the source and mode options

    source : 'V' or 'I'
    mode : 'single' or 'sweep'

    return
    list of dash core components
    """

    source_label, measure_label = get_source_labels(source)

    source_unit, measure_unit = get_source_units(source)

    h_style = {
        'display': 'flex',
        'flex-direction': 'row',
        'alignItems': 'center',
        'justifyContent': 'space-between',
        'margin': '5px'
    }

    if mode == 'single':
        # contains a know to adjust the source
        children_source_div = [
            daq.Knob(
                id='source-knob',
                value=0.0,
                label=source_label
            )
        ]

        mode_style = {
            'display': 'flex',
            'flex-direction': 'column',
            'alignItems': 'center'
        }

    else:
        # contains start, stop and step of the sweep
        children_source_div = [
            html.H4("%s sweep" % source_label),
            html.Div(
                [
                    html.H2('Start'),
                    html.Br(),
                    daq.PrecisionInput(
                        id='source-start',
                        precision=4,
                        label=' %s' % source_unit,
                        labelPosition='right'
                    )
                ],
                style=h_style
            ),
            html.Div(
                [
                    html.H2('Stop'),
                    daq.PrecisionInput(
                        id='source-stop',
                        precision=4,
                        label=' %s' % source_unit,
                        labelPosition='right'
                    )
                ],
                style=h_style
            ),
            html.Div(
                [
                    html.H2('Step'),
                    daq.PrecisionInput(
                        id='source-step',
                        precision=4,
                        label=' %s' % source_unit,
                        labelPosition='right'
                    )
                ],
                style=h_style
            )
        ]

        mode_style = {
            'display': 'flex',
            'flex-direction': 'column',
            'alignItems': 'center'
        }

    return [
        # source controls
        html.Div(
            id='source-div',
            className="three columns",
            children=children_source_div,
            style=mode_style
        ),
        # trigger measure button
        html.Div(
            id='trigger-div',
            className="two columns",
            children=[
                daq.StopButton(
                    id='trigger-measure',
                    buttonText='Measure %s' % mode
                )
            ]
        ),
        # display the measured value
        html.Div(
            id='measure-div',
            className="five columns",
            children=[
                daq.LEDDisplay(
                    id="source-display",
                    label='Applied %s (%s)' % (source_label, source_unit),
                    value="0.0000"
                ),
                daq.LEDDisplay(
                    id="measure-display",
                    label='Measured %s (%s)' % (measure_label, measure_unit),
                    value="0.0000"
                )
            ]
        )

    ]


# Create controls using a function
def generate_main_layout(theme='light'):
    """generate the layout of the app"""

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
                                'data': [],
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
                        html.H4('Sourcing :'),
                        dcc.RadioItems(
                            id='source-choice',
                            options=[
                                {'label': 'Voltage', 'value': 'V'},
                                {'label': 'Current', 'value': 'I'}
                            ],
                            value='V'
                        ),
                        html.Br(),
                        html.H4('Measure mode :'),
                        dcc.RadioItems(
                            id='mode-choice',
                            options=[
                                {'label': 'Single measure', 'value': 'single'},
                                {'label': 'Sweep', 'value': 'sweep'}
                            ],
                            value='single'
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
            children=generate_source_mode_layout(),
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
        dcc.Interval(id='refresher', interval=1000),
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
# generate the callbacks between the instrument and the app

@app.callback(
    Output('page-content', 'children'),
    [Input('toggleTheme', 'value')]
)
def page_layout(value):
    if value:
        return generate_main_layout('dark')
    else:
        return generate_main_layout('light')


@app.callback(
    Output('measure_controls', 'children'),
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
def source_choice_toggle(src_val, mode_val):
    """update the Radio Items choosing voltage or current source"""

    return generate_source_mode_layout(src_val, mode_val)


@app.callback(
    Output('page-content', 'style'),
    [Input('toggleTheme', 'value')],
    [State('page-content', 'style')]
)
def page_style(value, style_dict):

    if value:
        theme = 'dark'
    else:
        theme = 'light'

    style_dict['color'] = text_color[theme]
    style_dict['background'] = bkg_color[theme]

    return style_dict


@app.callback(
    Output('source-display', 'value'),
    [],
    [
        State('source-knob', 'value'),
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('trigger-measure', 'click')
    ]
)
def update_source_display(start, src_val, mode_val):
    """"read the source value from the instrument"""
    # initiate a measure of the KT2400
    # read the source value
    return start


@app.callback(
    Output('measure-display', 'value'),
    [
        Input('source-display', 'value')
    ],
    [
        State('source-knob', 'value'),
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ]
)
def update_measure_display(applied_src, start, src_val, mode_val):
    """"read the measured value from the instrument"""
    # check that the applied value correspond to source-knob
    # initiate a measure of the KT2400
    # read the measure value and return it
    return np.round(np.random.rand(), 4)


@app.callback(
    Output('IV_graph', 'figure'),
    [
        Input('toggleTheme', 'value')
    ],
    [
        State('source-knob', 'value'),
        State('source-choice', 'value'),
        State('mode-choice', 'value')
    ],
    [
        Event('trigger-measure', 'click')
    ]
)
def update_graph(theme, start, src_val, mode_val):
    """"update the IV graph"""
    if theme:
        theme = 'dark'
    else:
        theme = 'light'

    source_label, measure_label = get_source_labels(src_val)

    source_unit, measure_unit = get_source_units(src_val)

    if mode_val == 'single':
        pass
    else:
        pass
    xdata = 10 * np.squeeze(np.random.rand(10, 1))
    ydata = 10 * np.squeeze(np.random.rand(10, 1))
    print(xdata)
    print(ydata)
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
                'title': 'Applied %s (%s)' % (source_label, source_unit),
                'color': text_color[theme],
                'gridcolor': grid_color[theme]
            },
            yaxis={
                'title': 'Measured %s (%s)' % (measure_label, measure_unit),
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


# In[]:
# Main
if __name__ == '__main__':
    app.run_server(debug=True)
