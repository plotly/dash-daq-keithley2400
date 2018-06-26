# In[]:
# Import required libraries
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


# Create controls using a function
def generate_lab_layout(theme='light'):
    """generate the layout of the app from a list of instruments"""

    html_layout = [
        html.Div(
            className='row',
            children=[
                html.Div(
                    className="ten columns",
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
                                    )
                                )
                            }
                        )
                    ]
                )
            ]
        ),
        html.Div(
            id='graph_controls',
            className='row',
            children=[
                html.Div(
                    className="five columns",
                    children=[
                        daq.Knob(id='knob_V')
                    ],
                    style={'align': 'center'}
                ),
                html.Div(
                    className="five columns",
                    children=[
                        daq.Knob(id='knob_I')
                    ],
                    style={'align': 'center'}
                )
            ],
            style={'align': 'center'}
        ),
        html.Div(
            className='row',
            children=[
                html.Div(
                    id='',
                    className="five columns",
                    children=[
                        dcc.Graph(
                            id='A_graph',
                            figure={
                                'data': [],
                                'layout': dict(
                                    paper_bgcolor=bkg_color[theme],
                                    plot_bgcolor=bkg_color[theme],
                                    font=dict(
                                        color=text_color[theme],
                                        size=15,
                                    )
                                )
                            }
                        )
                    ]
                ),
                html.Div(
                    id='graph_controls',
                    className="five columns",
                    children=[
                        dcc.Graph(
                            id='B_graph',
                            figure={
                                'data': [],
                                'layout': dict(
                                    paper_bgcolor=bkg_color[theme],
                                    plot_bgcolor=bkg_color[theme],
                                    font=dict(
                                        color=text_color[theme],
                                        size=15,
                                    )
                                )
                            }
                        )
                    ]
                )
            ],
            style={
                'align': 'center',
                'border-margin': 'red'
            }
        ),
        html.Div(
            className='row',
            children=html.Div(
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
                    'max-width': '600px',
                    'margin': '15px auto 300 px auto',
                    'padding': '40px',
                    'alignItems': 'center',
                    'box-shadow': '10px 10px 5px rgba(0, 0, 0, 0.2)',
                    'border': '1px solid #DFE8F3',
                    'color': text_color[theme],
                    'background': bkg_color[theme]
                },
            )
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
        html.Div(
            id='header',
            className='banner',
            children=[
                html.H2('Dash DAQ: pressure gauge monitoring'),
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
            children=generate_lab_layout(theme=MY_THEME),
            className='ten columns',
            style={'width': '100%'}
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
    [Input('toggleTheme', 'value')])
def page_layout(value):
    if value:
        return generate_lab_layout('dark')
    else:
        return generate_lab_layout('light')


@app.callback(
    Output('page-content', 'style'),
    [Input('toggleTheme', 'value')],
    [State('page-content', 'style')]
)
def page_style(value, style_dict):
    print(style_dict)

    if value:
        theme = 'dark'
    else:
        theme = 'light'

    style_dict['color'] = text_color[theme]
    style_dict['background'] = bkg_color[theme]
    style_dict['border'] = '1px solid red'

    return style_dict


# @app.callback(
#     Output('graph', 'figure'),
#     [
#         Input('interval', 'n_intervals'),
#         Input('measuring', 'value'),
#         Input('%s_channel' % (pressure_gauge.unique_id()), 'value'),
#         Input('toggleTheme', 'value')
#     ])
# def update_graph(n_interval, is_measuring, selected_params, is_dark_theme):
#
#     if is_dark_theme:
#         theme = 'dark'
#     else:
#         theme = 'light'
#     # here one should write the script of what the instrument do
#     data_for_graph = []
#     for instr in instrument_rack:
#
#         # triggers the measure on the selected channels
#         if is_measuring:
#             for instr_channel in selected_params:
#                 instr.measure(instr_param='%s' % instr_channel)
#
#         # collects the data measured by all channels to update the graph
#         for instr_chan in selected_params:
#
#             idx_gauge = instr.measure_params.index(instr_chan)
#
#             if instr.measured_data[instr_chan]:
#                 xdata = 1000*instr.measured_data['%s_time' % instr_chan]
#                 ydata = instr.measured_data[instr_chan]
#                 data_for_graph.append(
#                     go.Scatter(
#                         x=xdata,
#                         y=ydata,
#                         mode='lines+markers',
#                         name='%s:%s' % (instr, instr_chan),
#                         line={
#                             'color': line_colors[idx_gauge],
#                             'width': 2
#                         }
#                     )
#                 )
#     # TODO should get the option of the graph to not override it every time
#
#     return {
#         'data': data_for_graph,
#         'layout': dict(
#             xaxis={
#                 'type': 'date',
#                 'title': 'Time',
#                 'color': text_color[theme],
#                 'gridcolor': grid_color[theme]
#             },
#             yaxis={
#                 'title': 'Pressure (mbar)',
#                 'gridcolor': grid_color[theme]
#             },
#             font=dict(
#                 color=text_color[theme],
#                 size=15,
#             ),
#             margin={'l': 100, 'b': 100, 't': 50, 'r': 20, 'pad': 0},
#             plot_bgcolor=bkg_color[theme],
#             paper_bgcolor='rgba(0,0,0,0)'
#         )
#     }


# In[]:
# Main
if __name__ == '__main__':
    app.run_server(debug=True)
