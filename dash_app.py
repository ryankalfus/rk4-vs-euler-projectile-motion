"""Dash app for the projectile motion simulation."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import dash
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, dcc, html


ROOT = Path(__file__).resolve().parent
SIM_PATH = ROOT / "projectile-motion-simulation.py"
PLOT_HEIGHT = 360


def load_simulation_module():
    """Load a fresh simulation module."""
    spec = importlib.util.spec_from_file_location("projectile_motion_simulation", SIM_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load simulation file: {SIM_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summary_card(title, stats):
    """Build one summary card."""
    return html.Div(
        [
            html.H3(title, style={"marginTop": "0"}),
            html.Div(
                [
                    metric_block("Range (m)", f"{stats['Range (m)']:.2f}"),
                    metric_block("Max height (m)", f"{stats['Max height (m)']:.2f}"),
                    metric_block("Time (s)", f"{stats['Time (s)']:.2f}"),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(3, minmax(0, 1fr))",
                    "gap": "12px",
                },
            ),
        ],
        style={
            "background": "white",
            "border": "1px solid #d9e2ec",
            "borderRadius": "12px",
            "padding": "16px",
            "boxShadow": "0 2px 10px rgba(15, 23, 42, 0.05)",
        },
    )


def metric_block(label, value):
    """Render one metric."""
    return html.Div(
        [
            html.Div(label, style={"fontSize": "0.85rem", "color": "#52606d"}),
            html.Div(value, style={"fontSize": "1.4rem", "fontWeight": "600"}),
        ]
    )


def prepare_series(series, log_x=False, log_y=False):
    """Filter data for plotting."""
    prepared = []
    for x_vals, y_vals, label in series:
        x_arr = np.asarray(x_vals, dtype=float)
        y_arr = np.asarray(y_vals, dtype=float)
        mask = np.isfinite(x_arr) & np.isfinite(y_arr)
        if log_x:
            mask &= x_arr > 0
        if log_y:
            mask &= y_arr > 0
        prepared.append((x_arr[mask], y_arr[mask], label))
    return prepared


def axis_range(values, log_scale=False, pad_fraction=0.06):
    """Compute a comfortable axis range."""
    if len(values) == 0:
        return None

    v_min = float(np.min(values))
    v_max = float(np.max(values))

    if log_scale:
        if v_min == v_max:
            v_min *= 0.8
            v_max *= 1.25
        return [np.log10(v_min), np.log10(v_max)]

    span = v_max - v_min
    pad = max(1e-9, pad_fraction * (span if span else 1.0))
    return [v_min - pad, v_max + pad]


def make_figure(series, xlabel, ylabel, title, *, log_x=False, log_y=False, show_rangeslider=False):
    """Build one fast Plotly figure."""
    prepared = prepare_series(series, log_x=log_x, log_y=log_y)

    fig = go.Figure()
    for x_vals, y_vals, label in prepared:
        fig.add_trace(
            go.Scattergl(
                x=x_vals,
                y=y_vals,
                mode="lines",
                name=label,
                line={"width": 3},
            )
        )

    x_arrays = [x_vals for x_vals, _, _ in prepared if len(x_vals)]
    y_arrays = [y_vals for _, y_vals, _ in prepared if len(y_vals)]
    x_all = np.concatenate(x_arrays) if x_arrays else np.array([], dtype=float)
    y_all = np.concatenate(y_arrays) if y_arrays else np.array([], dtype=float)

    fig.update_layout(
        title=title,
        template="plotly_white",
        height=PLOT_HEIGHT,
        margin={"l": 56, "r": 24, "t": 56, "b": 48},
        dragmode="zoom",
        hovermode="closest",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        uirevision=title,
    )
    fig.update_xaxes(
        title=xlabel,
        showgrid=True,
        zeroline=False,
        type="log" if log_x else "linear",
        rangeslider={"visible": show_rangeslider and not log_x},
        range=axis_range(x_all, log_scale=log_x),
    )
    fig.update_yaxes(
        title=ylabel,
        showgrid=True,
        zeroline=False,
        type="log" if log_y else "linear",
        range=axis_range(y_all, log_scale=log_y),
    )
    return fig


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Projectile Motion Explorer", style={"marginTop": "0"}),
                html.Div(
                    [
                        html.Label("Launch angle (degrees)"),
                        dcc.Slider(5, 85, 1, value=45, id="theta", updatemode="mouseup"),
                        html.Label("Initial speed (m/s)", style={"marginTop": "18px"}),
                        dcc.Slider(1, 60, 0.5, value=20, id="v0", updatemode="mouseup"),
                        html.Label("Initial height (m)", style={"marginTop": "18px"}),
                        dcc.Slider(0, 20, 0.5, value=0, id="y0", updatemode="mouseup"),
                        html.Label("Time step dt (s)", style={"marginTop": "18px"}),
                        dcc.RadioItems(
                            id="dt",
                            options=[
                                {"label": "0.2", "value": 0.2},
                                {"label": "0.1", "value": 0.1},
                                {"label": "0.05", "value": 0.05},
                                {"label": "0.025", "value": 0.025},
                                {"label": "0.0125", "value": 0.0125},
                            ],
                            value=0.1,
                            inline=True,
                            inputStyle={"marginLeft": "8px", "marginRight": "4px"},
                        ),
                        html.Label("Max simulation time (s)", style={"marginTop": "18px"}),
                        dcc.Slider(1, 20, 0.5, value=10, id="tmax", updatemode="mouseup"),
                        dcc.Checklist(
                            id="drag",
                            options=[{"label": "Use air resistance", "value": "drag"}],
                            value=["drag"],
                            style={"marginTop": "18px"},
                        ),
                    ]
                ),
            ],
            style={
                "width": "320px",
                "padding": "24px",
                "background": "#f8fafc",
                "borderRight": "1px solid #d9e2ec",
                "minHeight": "100vh",
                "boxSizing": "border-box",
                "position": "sticky",
                "top": "0",
                "alignSelf": "flex-start",
            },
        ),
        html.Div(
            [
                html.Div(id="summary-cards"),
                html.Div(
                    [
                        dcc.Graph(
                            id="trajectory-graph",
                            config={
                                "displaylogo": False,
                                "scrollZoom": True,
                                "doubleClick": "reset",
                            },
                            style={"height": f"{PLOT_HEIGHT}px"},
                        ),
                        dcc.Graph(
                            id="speed-graph",
                            config={
                                "displaylogo": False,
                                "scrollZoom": True,
                                "doubleClick": "reset",
                            },
                            style={"height": f"{PLOT_HEIGHT}px"},
                        ),
                        dcc.Graph(
                            id="height-graph",
                            config={
                                "displaylogo": False,
                                "scrollZoom": True,
                                "doubleClick": "reset",
                            },
                            style={"height": f"{PLOT_HEIGHT}px"},
                        ),
                        dcc.Graph(
                            id="error-graph",
                            config={
                                "displaylogo": False,
                                "scrollZoom": True,
                                "doubleClick": "reset",
                            },
                            style={"height": f"{PLOT_HEIGHT}px"},
                        ),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(2, minmax(0, 1fr))",
                        "gap": "18px",
                        "marginTop": "18px",
                    },
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="convergence-graph",
                            config={
                                "displaylogo": False,
                                "scrollZoom": True,
                                "doubleClick": "reset",
                            },
                            style={"height": f"{PLOT_HEIGHT}px"},
                        ),
                        html.Div(id="slope-summary"),
                    ],
                    style={"marginTop": "18px"},
                ),
                html.Div(id="analytical-summary", style={"marginTop": "18px"}),
                html.H2("Animation", style={"marginTop": "24px"}),
                html.Iframe(
                    id="animation-frame",
                    style={
                        "width": "100%",
                        "height": "620px",
                        "border": "1px solid #d9e2ec",
                        "borderRadius": "12px",
                        "background": "white",
                    },
                ),
            ],
            style={"flex": "1", "padding": "24px", "background": "#eef2f6"},
        ),
    ],
    style={"display": "flex", "fontFamily": "Avenir Next, Helvetica, Arial, sans-serif"},
)


@app.callback(
    Output("summary-cards", "children"),
    Output("trajectory-graph", "figure"),
    Output("speed-graph", "figure"),
    Output("height-graph", "figure"),
    Output("error-graph", "figure"),
    Output("convergence-graph", "figure"),
    Output("slope-summary", "children"),
    Output("analytical-summary", "children"),
    Output("animation-frame", "srcDoc"),
    Input("theta", "value"),
    Input("v0", "value"),
    Input("y0", "value"),
    Input("dt", "value"),
    Input("tmax", "value"),
    Input("drag", "value"),
)
def update_view(theta_deg, v0, y0, dt, t_max, drag_values):
    """Update all outputs when controls change."""
    sim = load_simulation_module()
    sim.theta_deg = float(theta_deg)
    sim.v0 = float(v0)
    sim.y0 = float(y0)
    sim.dt = float(dt)
    sim.t_max = float(t_max)
    sim.use_quadratic_drag = "drag" in (drag_values or [])

    t_rk, x_rk, y_rk, vx_rk, vy_rk = sim.simulate(sim.acceleration_with_drag, sim.rk4_step)
    t_eu, x_eu, y_eu, vx_eu, vy_eu = sim.simulate(sim.acceleration_with_drag, sim.euler_step)

    summary_children = html.Div(
        [
            summary_card("RK4", sim.summarize(t_rk, x_rk, y_rk)),
            summary_card("Euler", sim.summarize(t_eu, x_eu, y_eu)),
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(2, minmax(0, 1fr))",
            "gap": "18px",
        },
    )

    has_analytical = not sim.use_quadratic_drag
    analytical_results = None
    if has_analytical:
        analytical_results = sim.analytical_closed_form(sim.dt)
        t_an, x_an, y_an, vx_an, vy_an = analytical_results
        summary_children.children.append(summary_card("Analytical", sim.summarize(t_an, x_an, y_an)))

    trajectory_series = [
        (x_rk, y_rk, "RK4"),
        (x_eu, y_eu, "Euler"),
    ]
    speed_series = [
        (t_rk, np.hypot(vx_rk, vy_rk), "RK4"),
        (t_eu, np.hypot(vx_eu, vy_eu), "Euler"),
    ]
    height_series = [
        (t_rk, y_rk, "RK4"),
        (t_eu, y_eu, "Euler"),
    ]

    if has_analytical and analytical_results is not None:
        trajectory_series.append((x_an, y_an, "Analytical"))
        speed_series.append((t_an, np.hypot(vx_an, vy_an), "Analytical"))
        height_series.append((t_an, y_an, "Analytical"))

    dt_ref = max(1e-4, sim.dt / 50.0)
    t_ref, x_ref, y_ref, _, _ = sim.simulate_with_dt(
        sim.acceleration_with_drag,
        sim.rk4_step,
        dt_ref,
        sim.t_max,
        stop_at_ground=True,
    )
    t_rk_err, err_rk = sim.position_error_vs_time(t_rk, x_rk, y_rk, t_ref, x_ref, y_ref)
    t_eu_err, err_eu = sim.position_error_vs_time(t_eu, x_eu, y_eu, t_ref, x_ref, y_ref)

    dt_list, max_err_rk, max_err_eu = sim.run_convergence_study(sim.acceleration_with_drag)
    slope_summary = html.Div(
        [
            html.H3("Convergence"),
            html.P(f"RK4 slope: {sim.estimate_slope(dt_list, max_err_rk):.3f}"),
            html.P(f"Euler slope: {sim.estimate_slope(dt_list, max_err_eu):.3f}"),
        ],
        style={
            "background": "white",
            "border": "1px solid #d9e2ec",
            "borderRadius": "12px",
            "padding": "16px",
        },
    )

    analytical_summary = html.Div()
    animation_series = [
        (t_rk, x_rk, y_rk, "RK4"),
        (t_eu, x_eu, y_eu, "Euler"),
    ]
    animation_title = "RK4 vs Euler"

    if has_analytical and analytical_results is not None:
        _, err_rk_vs_an = sim.position_error_vs_time(t_rk, x_rk, y_rk, t_an, x_an, y_an)
        _, err_eu_vs_an = sim.position_error_vs_time(t_eu, x_eu, y_eu, t_an, x_an, y_an)
        analytical_summary = html.Div(
            [
                html.H3("Distance From Analytical"),
                html.P(f"RK4 max position difference: {float(np.max(err_rk_vs_an)):.6g} m"),
                html.P(f"Euler max position difference: {float(np.max(err_eu_vs_an)):.6g} m"),
            ],
            style={
                "background": "white",
                "border": "1px solid #d9e2ec",
                "borderRadius": "12px",
                "padding": "16px",
            },
        )
        animation_series.append((t_an, x_an, y_an, "Analytical"))
        animation_title = "RK4 vs Euler vs Analytical"

    animation_html = sim.build_animation(animation_series, animation_title).data

    return (
        summary_children,
        make_figure(trajectory_series, "x (m)", "y (m)", "Projectile Trajectory"),
        make_figure(speed_series, "time (s)", "speed (m/s)", "Speed vs Time", show_rangeslider=True),
        make_figure(height_series, "time (s)", "height y (m)", "Height vs Time", show_rangeslider=True),
        make_figure(
            [
                (t_rk_err, err_rk, "RK4 error"),
                (t_eu_err, err_eu, "Euler error"),
            ],
            "time (s)",
            "position error (m)",
            "Error vs Time (log-log)",
            log_x=True,
            log_y=True,
        ),
        make_figure(
            [
                (dt_list, max_err_rk, "RK4 max error"),
                (dt_list, max_err_eu, "Euler max error"),
            ],
            "timestep dt (s)",
            "max position error over time (m)",
            "Error vs Timestep Size (log-log)",
            log_x=True,
            log_y=True,
        ),
        slope_summary,
        analytical_summary,
        animation_html,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
