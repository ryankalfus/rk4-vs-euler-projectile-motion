"""Dash app for the projectile motion simulation."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import dash
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html


os.environ["MPLBACKEND"] = "Agg"

ROOT = Path(__file__).resolve().parent
SIM_PATH = ROOT / "projectile-motion-simulation.py"
PLOT_HEIGHT = 360

CONTROL_SPECS = {
    "theta": {"min": 5.0, "max": 85.0, "step": 0.001, "default": 45.0},
    "v0": {"min": 1.0, "max": 60.0, "step": 0.001, "default": 20.0},
    "y0": {"min": 0.0, "max": 20.0, "step": 0.001, "default": 0.0},
    "dt": {"min": 0.01, "max": 0.2, "step": 0.001, "default": 0.01},
    "drag-strength": {"min": 0.0, "max": 3.0, "step": 0.001, "default": 1.0},
    "tmax": {"min": 1.0, "max": 20.0, "step": 0.001, "default": 10.0},
}

TRACE_COLORS = {
    "RK4": "#5b6cff",
    "Euler": "#ef5b3f",
    "Analytical": "#7b8794",
    "RK4 max error": "#5b6cff",
    "Euler max error": "#ef5b3f",
    "RK4 vs analytical": "#5b6cff",
    "Euler vs analytical": "#ef5b3f",
}


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


def control_block(label, control_id):
    """Render one slider control with an editable value box."""
    spec = CONTROL_SPECS[control_id]
    return html.Div(
        [
            html.Div(
                [
                    html.Span(label),
                    dcc.Input(
                        id=f"{control_id}-input",
                        type="number",
                        value=spec["default"],
                        step=0.001,
                        debounce=True,
                        className="control-input control-input-white",
                    ),
                ],
                className="control-label-row",
            ),
            dcc.Input(
                id=control_id,
                type="range",
                min=spec["min"],
                max=spec["max"],
                step=spec["step"],
                value=spec["default"],
                className="control-slider",
            ),
        ],
        className="control-block",
    )


def graph_card(graph_id):
    """Wrap a graph in a simple card."""
    return html.Div(
        [
            dcc.Graph(
                id=graph_id,
                config={
                    "displaylogo": False,
                    "displayModeBar": "hover",
                    "scrollZoom": False,
                    "doubleClick": False,
                    "modeBarButtonsToRemove": [
                        "select2d",
                        "lasso2d",
                        "hoverClosestCartesian",
                        "hoverCompareCartesian",
                        "toggleSpikelines",
                        "toImage",
                    ],
                    "modeBarButtonsToAdd": [
                        "pan2d",
                    ],
                },
                style={"height": f"{PLOT_HEIGHT}px"},
            )
        ],
        id=f"{graph_id}-card",
        style={
            "background": "white",
            "border": "1px solid #d9e2ec",
            "borderRadius": "12px",
            "padding": "10px 12px 0 12px",
            "boxShadow": "0 2px 10px rgba(15, 23, 42, 0.05)",
            "overflow": "hidden",
        },
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


def running_max(values):
    """Return the running maximum of a 1D array."""
    return np.maximum.accumulate(np.asarray(values, dtype=float))


def apply_drag_strength(sim, drag_strength):
    """Scale the default drag settings."""
    sim.k_quad = 0.5 * sim.rho * sim.Cd * sim.A * float(drag_strength)


def trace_color(label, index):
    """Pick a stable color for a trace label."""
    if label in TRACE_COLORS:
        return TRACE_COLORS[label]
    fallback = ["#5b6cff", "#ef5b3f", "#2a9d8f", "#7b8794"]
    return fallback[index % len(fallback)]


def build_animation_panel_html(series_list):
    """Return a modern custom animation player as HTML."""
    payload = []
    x_max = 1.0
    y_max = 1.0
    t_max = 1.0

    for t_vals, x_vals, y_vals, label, color in series_list:
        t_arr = np.asarray(t_vals, dtype=float)
        x_arr = np.asarray(x_vals, dtype=float)
        y_arr = np.asarray(y_vals, dtype=float)
        n_points = len(t_arr)
        step = max(1, n_points // 320)
        idx = np.arange(0, n_points, step, dtype=int)
        if len(idx) == 0 or idx[-1] != n_points - 1:
            idx = np.append(idx, n_points - 1)

        t_use = t_arr[idx]
        x_use = x_arr[idx]
        y_use = y_arr[idx]
        payload.append(
            {
                "label": label,
                "color": color,
                "t": np.round(t_use, 4).tolist(),
                "x": np.round(x_use, 4).tolist(),
                "y": np.round(y_use, 4).tolist(),
            }
        )
        if len(x_use):
            x_max = max(x_max, float(np.max(x_use)))
            y_max = max(y_max, float(np.max(y_use)))
            t_max = max(t_max, float(t_use[-1]))

    data_json = json.dumps(payload)
    accent = "#4f6af0"

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {{
      margin: 0;
      font-family: "Avenir Next", Helvetica, Arial, sans-serif;
      background: radial-gradient(circle at top left, #f7fbff, #eef4fb 45%, #e5edf7 100%);
      color: #183153;
    }}
    .wrap {{
      height: 100vh;
      box-sizing: border-box;
      padding: 18px;
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: 14px;
    }}
    .topbar, .footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.76);
      border: 1px solid rgba(198, 211, 226, 0.9);
      border-radius: 18px;
      backdrop-filter: blur(10px);
    }}
    .title {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
      font-size: 1.06rem;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid rgba(198, 211, 226, 0.9);
      font-size: 0.92rem;
    }}
    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: {accent};
      display: inline-block;
    }}
    .legend {{
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.9rem;
    }}
    .scene {{
      position: relative;
      overflow: hidden;
      border-radius: 26px;
      border: 1px solid rgba(198, 211, 226, 0.9);
      background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(243,247,252,0.95) 62%, rgba(232,239,247,1) 100%);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.85);
    }}
    svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}
    .footer {{
      display: grid;
      grid-template-rows: auto auto;
      gap: 14px;
      width: 100%;
      min-width: 0;
      box-sizing: border-box;
    }}
    .scrub-row {{
      display: block;
      width: 100%;
      min-width: 0;
    }}
    .controls-row {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      width: 100%;
    }}
    button {{
      border: none;
      border-radius: 12px;
      padding: 10px 14px;
      background: #15345b;
      color: white;
      font-weight: 700;
      cursor: pointer;
      width: 96px;
      height: 40px;
      box-sizing: border-box;
      font-size: 0.96rem;
    }}
    button.secondary {{
      background: white;
      color: #15345b;
      border: 1px solid rgba(198, 211, 226, 0.9);
    }}
    input[type="range"] {{
      width: 100%;
      min-width: 0;
      accent-color: {accent};
    }}
    select {{
      border-radius: 12px;
      padding: 10px 12px;
      border: 1px solid rgba(198, 211, 226, 0.9);
      background: white;
      color: #15345b;
      font-weight: 700;
      font-family: inherit;
      width: 96px;
      height: 40px;
      box-sizing: border-box;
      font-size: 0.96rem;
    }}
    .timebox {{
      min-width: 92px;
      text-align: center;
      font-variant-numeric: tabular-nums;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div class="title">
        <span class="dot"></span>
        <span>2D Flight Comparison</span>
      </div>
      <div class="legend" id="legend"></div>
    </div>
    <div class="scene">
      <svg id="scene" viewBox="0 0 1200 620" preserveAspectRatio="xMidYMid meet"></svg>
    </div>
    <div class="footer">
      <div class="scrub-row">
        <input id="scrubber" type="range" min="0" max="1000" value="0" />
      </div>
      <div class="controls-row">
        <button id="playBtn">Pause</button>
        <button id="resetBtn" class="secondary">Restart</button>
        <select id="speedSelect" aria-label="Animation speed">
          <option value="0.25">0.25x</option>
          <option value="0.5">0.5x</option>
          <option value="0.75">0.75x</option>
          <option value="1" selected>1x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
          <option value="1.75">1.75x</option>
          <option value="2">2x</option>
        </select>
        <div class="timebox" id="timebox">00:00.00</div>
      </div>
    </div>
  </div>
  <script>
    const series = {data_json};
    const xMax = {x_max:.6f};
    const yMax = {y_max:.6f};
    const tMax = {t_max:.6f};
    const svg = document.getElementById("scene");
    const legend = document.getElementById("legend");
    const scrubber = document.getElementById("scrubber");
    const playBtn = document.getElementById("playBtn");
    const resetBtn = document.getElementById("resetBtn");
    const speedSelect = document.getElementById("speedSelect");
    const timebox = document.getElementById("timebox");
    let playing = true;
    let simTime = 0;
    let lastStamp = null;
    let playbackRate = 1;
    const margin = {{ left: 72, right: 40, top: 40, bottom: 70 }};
    const width = 1200;
    const height = 620;
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;

    const xToPx = (x) => margin.left + (x / Math.max(xMax, 1e-6)) * plotWidth;
    const yToPx = (y) => height - margin.bottom - (y / Math.max(yMax, 1e-6)) * plotHeight;

    function fmt(seconds) {{
      const totalHundredths = Math.round(seconds * 100);
      const minutes = Math.floor(totalHundredths / 6000);
      const rem = totalHundredths % 6000;
      const secs = Math.floor(rem / 100);
      const hundredths = rem % 100;
      return String(minutes).padStart(2, "0") + ":" + String(secs).padStart(2, "0") + "." + String(hundredths).padStart(2, "0");
    }}

    function interp(item, t) {{
      if (t <= item.t[0]) return {{ x: item.x[0], y: item.y[0], end: 0 }};
      if (t >= item.t[item.t.length - 1]) {{
        return {{ x: item.x[item.x.length - 1], y: item.y[item.y.length - 1], end: item.t.length - 1 }};
      }}
      let i = 1;
      while (i < item.t.length && item.t[i] < t) i++;
      const t0 = item.t[i - 1], t1 = item.t[i];
      const r = (t - t0) / (t1 - t0 || 1);
      return {{
        x: item.x[i - 1] + r * (item.x[i] - item.x[i - 1]),
        y: item.y[i - 1] + r * (item.y[i] - item.y[i - 1]),
        end: i
      }};
    }}

    function make(tag, attrs = {{}}, parent = svg) {{
      const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
      Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
      parent.appendChild(node);
      return node;
    }}

    make("rect", {{ x: 0, y: 0, width, height, fill: "transparent" }});
    make("rect", {{
      x: 0, y: yToPx(0), width, height: height - yToPx(0), fill: "rgba(120, 172, 110, 0.18)"
    }});
    make("line", {{
      x1: margin.left - 20, x2: width - margin.right + 20,
      y1: yToPx(0), y2: yToPx(0),
      stroke: "#577a57", "stroke-width": 4
    }});

    for (let i = 0; i <= 5; i++) {{
      const x = margin.left + (plotWidth * i / 5);
      make("line", {{
        x1: x, x2: x, y1: margin.top, y2: height - margin.bottom,
        stroke: "rgba(117, 142, 173, 0.14)", "stroke-width": 1
      }});
    }}

    const layers = series.map((item) => {{
      const trail = make("path", {{
        fill: "none", stroke: item.color, "stroke-width": 5, "stroke-linecap": "round", opacity: 0.35
      }});
      const glow = make("circle", {{ r: 18, fill: item.color, opacity: 0.12 }});
      const ball = make("circle", {{ r: 11, fill: item.color, stroke: "white", "stroke-width": 3 }});
      const chip = document.createElement("span");
      chip.className = "legend-item";
      chip.innerHTML = `<span class="dot" style="background:${{item.color}}"></span><span>${{item.label}}</span>`;
      legend.appendChild(chip);
      return {{ trail, glow, ball }};
    }});

    function render(t) {{
      series.forEach((item, idx) => {{
        const frame = interp(item, t);
        const end = Math.max(1, frame.end);
        const pts = [];
        for (let i = 0; i < end; i++) {{
          pts.push(`${{xToPx(item.x[i]).toFixed(2)}},${{yToPx(item.y[i]).toFixed(2)}}`);
        }}
        pts.push(`${{xToPx(frame.x).toFixed(2)}},${{yToPx(frame.y).toFixed(2)}}`);
        layers[idx].trail.setAttribute("d", "M " + pts.join(" L "));
        layers[idx].glow.setAttribute("cx", xToPx(frame.x));
        layers[idx].glow.setAttribute("cy", yToPx(frame.y));
        layers[idx].ball.setAttribute("cx", xToPx(frame.x));
        layers[idx].ball.setAttribute("cy", yToPx(frame.y));
      }});
      timebox.textContent = fmt(t);
      scrubber.value = Math.round((t / Math.max(tMax, 1e-6)) * 1000);
    }}

    function tick(stamp) {{
      if (lastStamp === null) lastStamp = stamp;
      const dt = (stamp - lastStamp) / 1000;
      lastStamp = stamp;
      if (playing) {{
        simTime = Math.min(tMax, simTime + dt * playbackRate);
        render(simTime);
        if (simTime >= tMax) {{
          playing = false;
          playBtn.textContent = "Play";
        }}
      }}
      requestAnimationFrame(tick);
    }}

    playBtn.addEventListener("click", () => {{
      playing = !playing;
      playBtn.textContent = playing ? "Pause" : "Play";
      lastStamp = null;
    }});

    resetBtn.addEventListener("click", () => {{
      simTime = 0;
      playing = true;
      playBtn.textContent = "Pause";
      lastStamp = null;
      render(simTime);
    }});

    speedSelect.addEventListener("change", (event) => {{
      playbackRate = Number(event.target.value) || 1;
    }});

    scrubber.addEventListener("input", (event) => {{
      simTime = (Number(event.target.value) / 1000) * tMax;
      playing = false;
      playBtn.textContent = "Play";
      lastStamp = null;
      render(simTime);
    }});

    render(0);
    requestAnimationFrame(tick);
  </script>
</body>
</html>"""


def make_figure(
    series,
    xlabel,
    ylabel,
    title,
    *,
    log_x=False,
    log_y=False,
    x_tickvals=None,
    x_ticktext=None,
):
    """Build one fast Plotly figure."""
    prepared = prepare_series(series, log_x=log_x, log_y=log_y)

    fig = go.Figure()
    for idx, (x_vals, y_vals, label) in enumerate(prepared):
        color = trace_color(label, idx)
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                name=label,
                line={"width": 3, "color": color},
                hovertemplate="(%{x:.4g}, %{y:.4g})<extra></extra>",
                hoverlabel={
                    "font": {"color": color, "size": 13},
                    "bgcolor": "rgba(255,255,255,0)",
                    "bordercolor": "rgba(255,255,255,0)",
                },
            )
        )

    x_arrays = [x_vals for x_vals, _, _ in prepared if len(x_vals)]
    y_arrays = [y_vals for _, y_vals, _ in prepared if len(y_vals)]
    x_all = np.concatenate(x_arrays) if x_arrays else np.array([], dtype=float)
    y_all = np.concatenate(y_arrays) if y_arrays else np.array([], dtype=float)

    fig.update_layout(
        template="plotly_white",
        height=PLOT_HEIGHT,
        margin={"l": 64, "r": 28, "t": 88, "b": 60},
        dragmode="zoom",
        hovermode="closest",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.04,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 12},
        },
        title={
            "text": f"<b>{title}</b>",
            "x": 0.02,
            "xanchor": "left",
            "y": 0.99,
            "yanchor": "top",
            "font": {"size": 12},
        },
        hoverlabel={"namelength": 0},
    )
    fig.update_xaxes(
        title=xlabel,
        showgrid=True,
        zeroline=False,
        type="log" if log_x else "linear",
        range=axis_range(x_all, log_scale=log_x),
        tickmode="array" if x_tickvals is not None else None,
        tickvals=x_tickvals,
        ticktext=x_ticktext,
    )
    fig.update_yaxes(
        title=ylabel,
        showgrid=True,
        zeroline=False,
        type="log" if log_y else "linear",
        range=axis_range(y_all, log_scale=log_y),
    )
    return fig


app = dash.Dash(__name__, assets_folder=str(ROOT / "assets"))
server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Projectile Motion", style={"marginTop": "0"}),
                html.Div(
                    [
                        control_block("Launch angle (degrees)", "theta"),
                        control_block("Initial speed (m/s)", "v0"),
                        control_block("Initial height (m)", "y0"),
                        control_block("Time step dt (s)", "dt"),
                        control_block("Drag coefficient", "drag-strength"),
                        control_block("Max simulation time (s)", "tmax"),
                        dcc.Checklist(
                            id="drag",
                            options=[{"label": "Use air resistance", "value": "drag"}],
                            value=["drag"],
                            className="drag-checklist",
                        ),
                        html.Button(
                            "Run Simulation",
                            id="run-button",
                            n_clicks=0,
                            style={
                                "marginTop": "20px",
                                "padding": "10px 14px",
                                "borderRadius": "10px",
                                "border": "none",
                                "background": "#1f77b4",
                                "color": "white",
                                "fontWeight": "600",
                                "cursor": "pointer",
                            },
                        ),
                    ]
                ),
            ],
            className="sidebar-panel",
        ),
        html.Div(
            [
                html.Div(id="summary-cards"),
                html.Div(
                    [
                        html.Div("Animation", className="animation-title"),
                        html.Iframe(
                            id="animation-frame",
                            style={
                                "width": "100%",
                                "height": "620px",
                                "border": "none",
                                "borderRadius": "22px",
                                "background": "transparent",
                            },
                        ),
                    ],
                    className="animation-shell",
                ),
                html.Div(
                    [
                        graph_card("trajectory-graph"),
                        graph_card("speed-graph"),
                        graph_card("height-graph"),
                        graph_card("error-graph"),
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
                        graph_card("analytical-summary")
                    ],
                    id="analytical-wrap",
                    style={"marginTop": "18px"},
                ),
            ],
            className="content-panel",
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("theta", "value"),
    Output("theta-input", "value"),
    Output("v0", "value"),
    Output("v0-input", "value"),
    Output("y0", "value"),
    Output("y0-input", "value"),
    Output("dt", "value"),
    Output("dt-input", "value"),
    Output("drag-strength", "value"),
    Output("drag-strength-input", "value"),
    Output("tmax", "value"),
    Output("tmax-input", "value"),
    Input("theta", "value"),
    Input("theta-input", "value"),
    Input("v0", "value"),
    Input("v0-input", "value"),
    Input("y0", "value"),
    Input("y0-input", "value"),
    Input("dt", "value"),
    Input("dt-input", "value"),
    Input("drag-strength", "value"),
    Input("drag-strength-input", "value"),
    Input("tmax", "value"),
    Input("tmax-input", "value"),
)
def sync_controls(
    theta,
    theta_input,
    v0,
    v0_input,
    y0,
    y0_input,
    dt,
    dt_input,
    drag_strength,
    drag_strength_input,
    tmax,
    tmax_input,
):
    """Keep sliders and editable inputs in sync."""
    ctx = dash.callback_context
    triggered = ctx.triggered_id

    def normalize(control_id, slider_value, input_value):
        spec = CONTROL_SPECS[control_id]
        if triggered == f"{control_id}-input" and input_value is not None:
            raw_value = input_value
        elif slider_value is not None:
            raw_value = slider_value
        elif input_value is not None:
            raw_value = input_value
        else:
            raw_value = spec["default"]

        value = round(float(raw_value), 3)
        value = min(spec["max"], max(spec["min"], value))
        return value, value

    theta_val = normalize("theta", theta, theta_input)
    v0_val = normalize("v0", v0, v0_input)
    y0_val = normalize("y0", y0, y0_input)
    dt_val = normalize("dt", dt, dt_input)
    drag_strength_val = normalize("drag-strength", drag_strength, drag_strength_input)
    tmax_val = normalize("tmax", tmax, tmax_input)

    return (
        *theta_val,
        *v0_val,
        *y0_val,
        *dt_val,
        *drag_strength_val,
        *tmax_val,
    )


@app.callback(
    Output("summary-cards", "children"),
    Output("trajectory-graph", "figure"),
    Output("speed-graph", "figure"),
    Output("height-graph", "figure"),
    Output("error-graph", "figure"),
    Output("analytical-summary", "figure"),
    Output("analytical-wrap", "style"),
    Output("animation-frame", "srcDoc"),
    Input("run-button", "n_clicks"),
    State("theta", "value"),
    State("v0", "value"),
    State("y0", "value"),
    State("dt", "value"),
    State("drag-strength", "value"),
    State("tmax", "value"),
    State("drag", "value"),
)
def update_view(_n_clicks, theta_deg, v0, y0, dt, drag_strength, t_max, drag_values):
    """Update all outputs when controls change."""
    sim = load_simulation_module()
    sim.theta_deg = float(theta_deg)
    sim.v0 = float(v0)
    sim.y0 = float(y0)
    sim.dt = float(dt)
    sim.t_max = float(t_max)
    sim.use_quadratic_drag = "drag" in (drag_values or [])
    apply_drag_strength(sim, drag_strength)

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

    analytical_figure = go.Figure()
    analytical_figure.update_layout(
        template="plotly_white",
        height=PLOT_HEIGHT,
        margin={"l": 56, "r": 24, "t": 56, "b": 48},
        title="Distance From Analytical",
    )
    analytical_figure.add_annotation(
        text="Turn air resistance off to compare against the analytical solution.",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 16},
    )
    analytical_figure.update_xaxes(visible=False)
    analytical_figure.update_yaxes(visible=False)

    animation_series = [
        (t_rk, x_rk, y_rk, "RK4", "#5b6cff"),
        (t_eu, x_eu, y_eu, "Euler", "#ef5b3f"),
    ]

    if has_analytical and analytical_results is not None:
        t_rk_an, err_rk_vs_an = sim.position_error_vs_time(t_rk, x_rk, y_rk, t_an, x_an, y_an)
        t_eu_an, err_eu_vs_an = sim.position_error_vs_time(t_eu, x_eu, y_eu, t_an, x_an, y_an)
        analytical_figure = make_figure(
            [
                (t_rk_an, err_rk_vs_an, "RK4 vs analytical"),
                (t_eu_an, err_eu_vs_an, "Euler vs analytical"),
            ],
            "time (s)",
            "position error (m)",
            "Distance From Analytical",
        )
    dt_list, max_err_rk, max_err_eu = sim.run_convergence_study(sim.acceleration_with_drag)
    slope_rk = sim.estimate_slope(dt_list, max_err_rk)
    slope_eu = sim.estimate_slope(dt_list, max_err_eu)
    convergence_title = (
        f"Error vs Timestep Size (log-log) | RK4 slope {slope_rk:.2f}, "
        f"Euler slope {slope_eu:.2f}"
    )
    dt_ticktext = [f"{dt_i:g}" for dt_i in dt_list]

    animation_html = build_animation_panel_html(animation_series)

    return (
        summary_children,
        make_figure(trajectory_series, "x (m)", "y (m)", "Projectile Trajectory"),
        make_figure(speed_series, "time (s)", "speed (m/s)", "Speed vs Time"),
        make_figure(height_series, "time (s)", "height y (m)", "Height vs Time"),
        make_figure(
            [
                (dt_list, max_err_rk, "RK4 max error"),
                (dt_list, max_err_eu, "Euler max error"),
            ],
            "timestep dt (s)",
            "max position error over time (m)",
            convergence_title,
            log_x=True,
            log_y=True,
            x_tickvals=dt_list,
            x_ticktext=dt_ticktext,
        ),
        analytical_figure,
        {"marginTop": "18px"} if has_analytical else {"display": "none"},
        animation_html,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
