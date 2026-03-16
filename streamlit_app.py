"""Interactive browser app for the projectile motion simulation."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parent
SIM_PATH = ROOT / "projectile-motion-simulation.py"
PLOT_HEIGHT = 360


def load_simulation_module():
    """Load a fresh copy of the simulation module for each app run."""
    spec = importlib.util.spec_from_file_location(
        "projectile_motion_simulation",
        SIM_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load simulation file: {SIM_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_interactive_figure(
    series,
    xlabel,
    ylabel,
    title,
    *,
    log_x=False,
    log_y=False,
    show_rangeslider=False,
):
    """Build an interactive Plotly figure with zoom and pan support."""
    fig = go.Figure()
    processed_series = []
    for x_vals, y_vals, label in series:
        x_vals = np.asarray(x_vals, dtype=float)
        y_vals = np.asarray(y_vals, dtype=float)

        mask = np.isfinite(x_vals) & np.isfinite(y_vals)
        if log_x:
            mask &= x_vals > 0
        if log_y:
            mask &= y_vals > 0

        x_use = x_vals[mask]
        y_use = y_vals[mask]
        processed_series.append((x_use, y_use, label))

        fig.add_trace(
            go.Scatter(
                x=x_use,
                y=y_use,
                mode="lines",
                name=label,
            )
        )

    axis_template = dict(
        title=xlabel,
        showgrid=True,
        zeroline=False,
    )
    y_axis_template = dict(
        title=ylabel,
        showgrid=True,
        zeroline=False,
    )

    if log_x:
        axis_template["type"] = "log"
    if log_y:
        y_axis_template["type"] = "log"

    fig.update_layout(
        title=title,
        height=PLOT_HEIGHT,
        margin=dict(l=20, r=20, t=55, b=20),
        template="plotly_white",
        dragmode="pan",
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )
    fig.update_xaxes(**axis_template)
    fig.update_yaxes(**y_axis_template)

    if show_rangeslider and not log_x:
        fig.update_xaxes(rangeslider=dict(visible=True))

    x_arrays = [x_vals for x_vals, _, _ in processed_series if len(x_vals)]
    y_arrays = [y_vals for _, y_vals, _ in processed_series if len(y_vals)]
    x_all = np.concatenate(x_arrays) if x_arrays else np.array([], dtype=float)
    y_all = np.concatenate(y_arrays) if y_arrays else np.array([], dtype=float)

    if len(x_all):
        if log_x:
            x_min = float(x_all.min())
            x_max = float(x_all.max())
            if x_min == x_max:
                x_min *= 0.8
                x_max *= 1.25
            fig.update_xaxes(range=[np.log10(x_min), np.log10(x_max)])
        else:
            x_pad = max(1e-9, 0.05 * (x_all.max() - x_all.min() or 1.0))
            fig.update_xaxes(range=[x_all.min() - x_pad, x_all.max() + x_pad])

    if len(y_all):
        if log_y:
            y_min = float(y_all.min())
            y_max = float(y_all.max())
            if y_min == y_max:
                y_min *= 0.8
                y_max *= 1.25
            fig.update_yaxes(range=[np.log10(y_min), np.log10(y_max)])
        else:
            y_pad = max(1e-9, 0.08 * (y_all.max() - y_all.min() or 1.0))
            fig.update_yaxes(range=[y_all.min() - y_pad, y_all.max() + y_pad])

    return fig


def show_figure(fig):
    """Render an interactive figure with consistent controls."""
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": True,
            "modeBarButtonsToAdd": [
                "zoom2d",
                "pan2d",
                "zoomIn2d",
                "zoomOut2d",
                "autoScale2d",
                "resetScale2d",
            ],
        },
    )


def show_summary(title, stats):
    """Render the main metrics for one method."""
    with st.container(border=True):
        st.subheader(title)
        col1, col2, col3 = st.columns(3)
        col1.metric("Range (m)", f"{stats['Range (m)']:.2f}")
        col2.metric("Max height (m)", f"{stats['Max height (m)']:.2f}")
        col3.metric("Time (s)", f"{stats['Time (s)']:.2f}")


st.set_page_config(page_title="Projectile Motion Explorer", layout="wide")
st.title("Projectile Motion Explorer")

with st.sidebar:
    st.header("Controls")
    theta_deg = st.slider("Launch angle (degrees)", 5, 85, 45)
    v0 = st.slider("Initial speed (m/s)", 1.0, 60.0, 20.0, 0.5)
    y0 = st.slider("Initial height (m)", 0.0, 20.0, 0.0, 0.5)
    dt = st.select_slider(
        "Time step dt (s)",
        options=[0.2, 0.1, 0.05, 0.025, 0.0125],
        value=0.1,
    )
    t_max = st.slider("Max simulation time (s)", 1.0, 20.0, 10.0, 0.5)
    use_quadratic_drag = st.checkbox("Use air resistance", value=True)

sim = load_simulation_module()
sim.theta_deg = float(theta_deg)
sim.v0 = float(v0)
sim.y0 = float(y0)
sim.dt = float(dt)
sim.t_max = float(t_max)
sim.use_quadratic_drag = bool(use_quadratic_drag)

t_rk, x_rk, y_rk, vx_rk, vy_rk = sim.simulate(sim.acceleration_with_drag, sim.rk4_step)
t_eu, x_eu, y_eu, vx_eu, vy_eu = sim.simulate(sim.acceleration_with_drag, sim.euler_step)

summary_col1, summary_col2 = st.columns(2)
with summary_col1:
    show_summary("RK4", sim.summarize(t_rk, x_rk, y_rk))
with summary_col2:
    show_summary("Euler", sim.summarize(t_eu, x_eu, y_eu))

has_analytical = not sim.use_quadratic_drag
analytical_results = None

if has_analytical:
    analytical_results = sim.analytical_closed_form(sim.dt)
    t_an, x_an, y_an, vx_an, vy_an = analytical_results
    show_summary("Analytical", sim.summarize(t_an, x_an, y_an))

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

plot_col1, plot_col2 = st.columns(2)
with plot_col1:
    show_figure(
        make_interactive_figure(
            trajectory_series,
            "x (m)",
            "y (m)",
            "Projectile Trajectory",
        )
    )
    show_figure(
        make_interactive_figure(
            height_series,
            "time (s)",
            "height y (m)",
            "Height vs Time",
            show_rangeslider=True,
        )
    )

with plot_col2:
    show_figure(
        make_interactive_figure(
            speed_series,
            "time (s)",
            "speed (m/s)",
            "Speed vs Time",
            show_rangeslider=True,
        )
    )

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

    show_figure(
        make_interactive_figure(
            [
                (t_rk_err, err_rk, "RK4 error"),
                (t_eu_err, err_eu, "Euler error"),
            ],
            "time (s)",
            "position error (m)",
            "Error vs Time (log-log)",
            log_x=True,
            log_y=True,
        )
    )

st.subheader("Convergence")
dt_list, max_err_rk, max_err_eu = sim.run_convergence_study(sim.acceleration_with_drag)
show_figure(
    make_interactive_figure(
        [
            (dt_list, max_err_rk, "RK4 max error"),
            (dt_list, max_err_eu, "Euler max error"),
        ],
        "timestep dt (s)",
        "max position error over time (m)",
        "Error vs Timestep Size (log-log)",
        log_x=True,
        log_y=True,
    )
)

col1, col2 = st.columns(2)
col1.metric("RK4 slope", f"{sim.estimate_slope(dt_list, max_err_rk):.3f}")
col2.metric("Euler slope", f"{sim.estimate_slope(dt_list, max_err_eu):.3f}")

if has_analytical and analytical_results is not None:
    _, err_rk_vs_an = sim.position_error_vs_time(t_rk, x_rk, y_rk, t_an, x_an, y_an)
    _, err_eu_vs_an = sim.position_error_vs_time(t_eu, x_eu, y_eu, t_an, x_an, y_an)

    st.subheader("Distance From Analytical")
    analytical_col1, analytical_col2 = st.columns(2)
    analytical_col1.metric(
        "RK4 max position difference (m)",
        f"{float(np.max(err_rk_vs_an)):.6g}",
    )
    analytical_col2.metric(
        "Euler max position difference (m)",
        f"{float(np.max(err_eu_vs_an)):.6g}",
    )

st.subheader("Animation")
animation_series = [
    (t_rk, x_rk, y_rk, "RK4"),
    (t_eu, x_eu, y_eu, "Euler"),
]
animation_title = "RK4 vs Euler"

if has_analytical and analytical_results is not None:
    animation_series.append((t_an, x_an, y_an, "Analytical"))
    animation_title = "RK4 vs Euler vs Analytical"

animation_html = sim.build_animation(animation_series, animation_title)
components.html(animation_html.data, height=560, scrolling=False)
