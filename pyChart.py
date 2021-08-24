import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go

from dash.dependencies import Input, Output
from datetime import timedelta


def axes_graph(candle_time, period_candle_past, period_candle_future, factor_price, time, close):
    if len(candle_time) == 2:
        minute_candle_past = int(candle_time[0]) * period_candle_past
        minute_candle_future = int(
            candle_time[0]) * period_candle_future

    else:

        minute_candle_past = int(candle_time[:2]) * period_candle_past
        minute_candle_future = int(
            candle_time[:2]) * period_candle_future

    time_update_x1 = time[-1] - \
        timedelta(minutes=minute_candle_past)
    time_update_x2 = time[-1] + \
        timedelta(minutes=minute_candle_future)

    window_price_array = close[time.index(
        time_update_x1): len(close)]

    price_update_max = max(window_price_array) + \
        max(window_price_array)*factor_price
    price_update_min = min(window_price_array) - \
        min(window_price_array)*factor_price

    return time_update_x1, time_update_x2, price_update_min, price_update_max


def plot(symbol, candle_time, graph, times, closes, opens=None, highs=None, lows=None, reg_close=None):

    INCREASING_COLOR = 'green'
    DECREASING_COLOR = 'red'

    app = dash.Dash(__name__)
    app.config.suppress_callback_exceptions = True
    # Define the app
    app.layout = html.Div(children=[
        html.Div(className='row', children=[
            html.Div(className='two columns div-user-controls', children=[
                html.H2(f'{symbol} - STOCK PRICES'),

            ]
            ),
            html.Div(
                className='ten columns div-for-charts bg-grey',  # Define the right element
                children=[
                    dcc.Graph(id='live-graph',
                              animate=True),
                    dcc.Interval(
                        id='graph-update',
                        interval=1000,
                        n_intervals=0
                    ),
                ]
            )

        ])
    ])

    @app.callback(
        Output('live-graph', 'figure'),
        [Input('graph-update', 'n_intervals'),
         ],
    )
    def update_graph_scatter(n):

        fig = go.Figure()

        if graph == 'lr':
            _factor_price = 0.01
            _period_candle_past = 250
            _period_candle_future = 30
            fig.add_trace(
                go.Scatter(
                    name="Linear Regression ",
                    hoverlabel=dict(font=dict(size=16), align="right"),
                    x=times,
                    y=reg_close,
                    mode="lines",
                    line=dict(color="white", width=3), yaxis="y1", hovertemplate="LR: %{y:$.5f}" + "<extra></extra>")
            )

            x1, x2, y1, y2 = axes_graph(
                candle_time, _period_candle_past, _period_candle_future, _factor_price, times, reg_close)

        else:
            _factor_price = 0.02
            _period_candle_past = 100
            _period_candle_future = 8
            fig.add_trace(
                go.Candlestick(
                    name=str(symbol),
                    type='candlestick',
                    showlegend=False,
                    hoverlabel=dict(font=dict(size=16),
                                    align="left", namelength=0),
                    x=times,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes,
                    decreasing=dict(line=dict(color="red"), fillcolor="red"),
                    increasing=dict(line=dict(color="forestgreen"),
                                    fillcolor="forestgreen")
                ),
            )
            x1, x2, y1, y2 = axes_graph(
                candle_time, _period_candle_past, _period_candle_future, _factor_price, times, closes)

        fig.update_layout(
            height=880,
            template='plotly_dark',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin={'t': 40},
            hovermode='x',
            autosize=True,
            xaxis_rangeslider_visible=False,
            xaxis={
                "title": "<b>Time</b>",
                "color": "white",
                "showline": True,
                "showgrid": True,
                "showticklabels": True,
                "linecolor": "white",
                "linewidth": 1,
                "ticks": "outside",
                "tickfont": {
                    "family": "Aerial",
                    "color": "white",
                    "size": 12
                },
                'range': [x1, x2],
            },
            yaxis={
                "title": "<b>Price</b>",
                "color": "white",
                "showline": True,
                "showgrid": True,
                "showticklabels": True,
                "linecolor": "white",
                "linewidth": 1,
                "ticks": "outside",
                "tickfont": {
                    "family": "Aerial",
                    "color": "white",
                    "size": 12
                },
                'range': [y1, y2]

            },
            font={
                "family": "sans-serif",
                "color": "white",
                "size": 12
            },

        )

        return fig

    app.run_server(debug=True)


""" 
fig={
            "data": [
                go.Candlestick(
                    x=times,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes,
                    increasing=dict(line=dict(color="green")),
                    decreasing=dict(line=dict(color="red")),
                ),
            ],
            "layout": go.Layout(
                xaxis={
                    "title": "<b>Time</b>",
                    "color": "white",
                    "showline": True,
                    "showgrid": True,
                    "showticklabels": True,
                    "linecolor": "white",
                    "linewidth": 1,
                    "ticks": "outside",
                    "tickfont": {
                        "family": "Aerial",
                        "color": "white",
                        "size": 12
                    },
                    'range': [time_update_x1, time_update_x2],
                },
                yaxis={
                    "title": "<b>Price</b>",
                    "color": "white",
                    "showline": True,
                    "showgrid": True,
                    "showticklabels": True,
                    "linecolor": "white",
                    "linewidth": 1,
                    "ticks": "outside",
                    "tickfont": {
                        "family": "Aerial",
                        "color": "white",
                        "size": 12
                    },
                    'range': [price_update_min, price_update_max]

                },
                font={
                    "family": "sans-serif",
                    "color": "white",
                    "size": 12
                },

                height=880,
                template='plotly_dark',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                margin={'t': 40},
                hovermode='x',
                autosize=True,
                xaxis_rangeslider_visible=False
            )
        } """
