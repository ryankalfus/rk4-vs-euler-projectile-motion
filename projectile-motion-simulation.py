"""Compare Euler and RK4 for 2D projectile motion."""

import numpy as np

try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
except Exception:  # pragma: no cover - optional for notebook/local plotting only.
    plt = None
    FuncAnimation = None

try:
    from IPython.display import HTML, display
except Exception:  # pragma: no cover - optional for notebook/local animation only.
    HTML = None
    display = None


# Parameters you can change.
g = 9.81                  # m/s^2
theta_deg = 45            # launch angle in degrees
v0 = 20.0                 # initial speed (m/s)
y0 = 0.0                  # initial height (m)
use_quadratic_drag = True
dt = 0.1                  # time step (s)
t_max = 10.0              # max simulation time (s)

# Physical constants.
m = 0.145                 # mass (kg) ~ baseball
rho = 1.225               # air density (kg/m^3)
Cd = 0.47                 # drag coefficient (~sphere)
r = 0.0366                # radius (m) ~ baseball
A = np.pi * r**2          # cross-sectional area (m^2)
k_quad = 0.5 * rho * Cd * A

# Exposed at the end so notebook users can inspect the latest run.
LAST_RESULTS = {}


def acceleration_with_drag(vx, vy):
    """Return acceleration components for the current velocity."""
    if use_quadratic_drag:
        speed = np.hypot(vx, vy)
        ax = -(k_quad / m) * speed * vx
        ay = -g - (k_quad / m) * speed * vy
        return ax, ay

    return 0.0, -g


def euler_step(state, dt_local, accel_func):
    """Advance the state by one Forward Euler step."""
    x, y, vx, vy = state
    ax, ay = accel_func(vx, vy)

    x_new = x + dt_local * vx
    y_new = y + dt_local * vy
    vx_new = vx + dt_local * ax
    vy_new = vy + dt_local * ay

    return np.array([x_new, y_new, vx_new, vy_new], dtype=float)


def rk4_step(state, dt_local, accel_func):
    """Advance the state by one RK4 step."""

    def derivative(step_state):
        _, _, vx, vy = step_state
        ax, ay = accel_func(vx, vy)
        return np.array([vx, vy, ax, ay], dtype=float)

    k1 = derivative(state)
    k2 = derivative(state + 0.5 * dt_local * k1)
    k3 = derivative(state + 0.5 * dt_local * k2)
    k4 = derivative(state + dt_local * k3)
    return state + (dt_local / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def initial_state():
    """Build the starting state vector."""
    theta = np.deg2rad(theta_deg)
    vx0 = v0 * np.cos(theta)
    vy0 = v0 * np.sin(theta)
    return np.array([0.0, y0, vx0, vy0], dtype=float)


def append_landing_point(t_vals, x_vals, y_vals, vx_vals, vy_vals, state, current_t):
    """Interpolate the ground hit so landing time and range look cleaner."""
    x_prev, y_prev = x_vals[-1], y_vals[-1]
    vx_prev, vy_prev = vx_vals[-1], vy_vals[-1]
    x_new, y_new = state[0], state[1]
    dt_step = current_t - t_vals[-1]

    if not use_quadratic_drag:
        disc = max(0.0, float(vy_prev**2 + 2.0 * g * y_prev))
        tau = (vy_prev + np.sqrt(disc)) / g if g != 0 else dt_step
        tau = min(max(float(tau), 0.0), dt_step)

        x_land = x_prev + vx_prev * tau
        t_land = t_vals[-1] + tau
        vx_land = vx_prev
        vy_land = vy_prev - g * tau
    else:
        denom = y_prev - y_new
        frac = (y_prev / denom) if denom != 0 else 1.0
        frac = min(max(float(frac), 0.0), 1.0)

        x_land = x_prev + frac * (x_new - x_prev)
        t_land = t_vals[-1] + frac * dt_step
        vx_land = vx_prev + frac * (state[2] - vx_prev)
        vy_land = vy_prev + frac * (state[3] - vy_prev)

    t_vals.append(t_land)
    x_vals.append(x_land)
    y_vals.append(0.0)
    vx_vals.append(vx_land)
    vy_vals.append(vy_land)


def simulate_projectile(accel_func, step_func, dt_local=dt, t_max_local=t_max, stop_at_ground=True):
    """Run the projectile simulation and return time, position, and velocity arrays."""
    state = initial_state()

    t_vals = [0.0]
    x_vals = [state[0]]
    y_vals = [state[1]]
    vx_vals = [state[2]]
    vy_vals = [state[3]]

    current_t = 0.0
    for _ in range(int(t_max_local / dt_local)):
        state = step_func(state, dt_local, accel_func)
        current_t += dt_local

        crossed_ground = stop_at_ground and state[1] < 0 and current_t > dt_local
        if crossed_ground:
            append_landing_point(
                t_vals,
                x_vals,
                y_vals,
                vx_vals,
                vy_vals,
                state,
                current_t,
            )
            break

        t_vals.append(current_t)
        x_vals.append(state[0])
        y_vals.append(state[1])
        vx_vals.append(state[2])
        vy_vals.append(state[3])

    return (
        np.array(t_vals, dtype=float),
        np.array(x_vals, dtype=float),
        np.array(y_vals, dtype=float),
        np.array(vx_vals, dtype=float),
        np.array(vy_vals, dtype=float),
    )


def simulate(accel_func, step_func):
    """Compatibility wrapper using the default timestep settings."""
    return simulate_projectile(accel_func, step_func, dt, t_max, stop_at_ground=True)


def simulate_with_dt(accel_func, step_func, dt_local, t_max_local, stop_at_ground=True):
    """Compatibility wrapper for timestep studies."""
    return simulate_projectile(
        accel_func,
        step_func,
        dt_local,
        t_max_local,
        stop_at_ground=stop_at_ground,
    )


def position_error_vs_time(t, x, y, t_ref, x_ref, y_ref):
    """Compare one trajectory against a reference trajectory."""
    t_end = min(float(t[-1]), float(t_ref[-1]))
    mask = t <= t_end
    t_use = t[mask]
    x_use = x[mask]
    y_use = y[mask]

    x_ref_interp = np.interp(t_use, t_ref, x_ref)
    y_ref_interp = np.interp(t_use, t_ref, y_ref)
    err = np.hypot(x_use - x_ref_interp, y_use - y_ref_interp)

    return t_use, err


def analytical_closed_form(dt_local):
    """Return the exact no-drag solution sampled at the requested timestep."""
    theta = np.deg2rad(theta_deg)
    vx0 = v0 * np.cos(theta)
    vy0 = v0 * np.sin(theta)

    disc = max(0.0, float(vy0**2 + 2.0 * g * y0))
    t_land = (vy0 + np.sqrt(disc)) / g if g != 0 else 0.0

    if t_land <= 0:
        t_vals = np.array([0.0], dtype=float)
    else:
        n_steps = int(np.floor(t_land / dt_local))
        t_vals = np.arange(0.0, (n_steps + 1) * dt_local + 1e-15, dt_local, dtype=float)
        if t_vals[-1] < t_land - 1e-12:
            t_vals = np.append(t_vals, t_land)
        else:
            t_vals[-1] = t_land

    return analytical_closed_form_at_times(t_vals)


def analytical_closed_form_at_times(t_vals):
    """Return the exact no-drag solution at the requested times."""
    theta = np.deg2rad(theta_deg)
    vx0 = v0 * np.cos(theta)
    vy0 = v0 * np.sin(theta)

    disc = max(0.0, float(vy0**2 + 2.0 * g * y0))
    t_land = (vy0 + np.sqrt(disc)) / g if g != 0 else 0.0
    t_arr = np.asarray(t_vals, dtype=float)
    t_clamped = np.clip(t_arr, 0.0, t_land)

    x_vals = vx0 * t_clamped
    y_vals = np.maximum(y0 + vy0 * t_clamped - 0.5 * g * t_clamped**2, 0.0)
    vx_vals = np.full_like(t_clamped, vx0, dtype=float)
    vy_vals = vy0 - g * t_clamped

    return t_clamped, x_vals, y_vals, vx_vals, vy_vals


def analytical_position_error_vs_time(t, x, y):
    """Compare a no-drag trajectory against the exact analytical solution."""
    t_use = np.asarray(t, dtype=float)
    _, x_ref, y_ref, _, _ = analytical_closed_form_at_times(t_use)
    err = np.hypot(np.asarray(x, dtype=float) - x_ref, np.asarray(y, dtype=float) - y_ref)
    return t_use, err


def format_mm_ss_hh(seconds_float):
    """Format seconds as mm:ss.hh for the animation timer."""
    total_hundredths = int(round(seconds_float * 100))
    minutes = total_hundredths // (60 * 100)
    rem = total_hundredths % (60 * 100)
    secs = rem // 100
    hundredths = rem % 100
    return f"{minutes:02d}:{secs:02d}.{hundredths:02d}"


def downsample_series(t_vals, x_vals, y_vals, target=400):
    """Keep animations lighter by showing fewer points."""
    n_points = len(t_vals)
    step = max(1, n_points // target)
    t_down = t_vals[::step]
    x_down = x_vals[::step]
    y_down = y_vals[::step]

    if len(t_down) == 0 or t_down[-1] != t_vals[-1]:
        t_down = np.append(t_down, t_vals[-1])
        x_down = np.append(x_down, x_vals[-1])
        y_down = np.append(y_down, y_vals[-1])

    return t_down, x_down, y_down


def build_animation(series_list, title):
    """Create a simple overlay animation for multiple trajectories."""
    if plt is None or FuncAnimation is None or HTML is None:
        raise RuntimeError("Animation support requires matplotlib and IPython.")

    downsampled = [
        (*downsample_series(t_vals, x_vals, y_vals), label)
        for t_vals, x_vals, y_vals, label in series_list
    ]
    frames = min(len(t_vals) for t_vals, _, _, _ in downsampled)
    total_duration = float(downsampled[0][0][frames - 1] - downsampled[0][0][0]) if frames else 0.0
    interval_ms = max(1, int(round(1000.0 * total_duration / max(frames - 1, 1))))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_axis_off()
    ax.set_aspect("equal", adjustable="box")

    if frames:
        x_max = float(max(np.max(x_vals[:frames]) for _, x_vals, _, _ in downsampled))
        y_max = float(max(np.max(y_vals[:frames]) for _, _, y_vals, _ in downsampled))
    else:
        x_max = 1.0
        y_max = 1.0

    ax.set_xlim(-0.05 * x_max, 1.05 * x_max)
    ax.set_ylim(-0.10 * max(1.0, y_max), 1.10 * max(1.0, y_max))
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [0, 0], linewidth=2)

    trails = []
    balls = []
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for idx, (_, _, _, label) in enumerate(downsampled):
        color = colors[idx % len(colors)]
        trail, = ax.plot([], [], linewidth=2, alpha=0.45, color=color, label=label)
        ball, = ax.plot([], [], marker="o", markersize=12, color=color)
        trails.append(trail)
        balls.append(ball)

    time_text = ax.text(0.02, 0.90, "", transform=ax.transAxes, fontsize=14, va="top")
    title_text = ax.text(
        0.5,
        0.95,
        title,
        transform=ax.transAxes,
        fontsize=14,
        va="top",
        ha="center",
    )

    fig.subplots_adjust(bottom=0.05, top=0.98, left=0.04, right=0.98)
    legend = ax.legend(
        handles=trails,
        loc="upper right",
        bbox_to_anchor=(0.98, 0.82),
        frameon=True,
        ncol=1,
        handlelength=2.0,
        borderaxespad=0.0,
    )
    legend.set_title("Method")

    def init():
        for trail in trails:
            trail.set_data([], [])
        for ball in balls:
            ball.set_data([], [])
        time_text.set_text("")
        return (*trails, *balls, time_text, title_text)

    def update(frame_idx):
        for series_idx, (t_vals, x_vals, y_vals, _) in enumerate(downsampled):
            trails[series_idx].set_data(x_vals[: frame_idx + 1], y_vals[: frame_idx + 1])
            balls[series_idx].set_data([x_vals[frame_idx]], [y_vals[frame_idx]])

        time_text.set_text(f"t = {format_mm_ss_hh(downsampled[0][0][frame_idx])}")
        return (*trails, *balls, time_text, title_text)

    animation = FuncAnimation(
        fig,
        update,
        frames=frames,
        init_func=init,
        interval=interval_ms,
        blit=True,
    )
    plt.close(fig)
    return HTML(animation.to_jshtml())


def summarize(t_vals, x_vals, y_vals):
    """Return a few easy-to-read metrics."""
    return {
        "Range (m)": float(x_vals[-1]),
        "Max height (m)": float(np.max(y_vals)),
        "Time (s)": float(t_vals[-1]),
    }


def print_summary(name, stats):
    """Print one summary line for an integrator or reference solution."""
    print(
        f"{name:<10} Range: {stats['Range (m)']:.2f} m | "
        f"Max height: {stats['Max height (m)']:.2f} m | "
        f"Time: {stats['Time (s)']:.2f} s"
    )


def plot_series(y_series, xlabel, ylabel, title):
    """Plot one or more lines with the same axes."""
    if plt is None:
        raise RuntimeError("Plotting requires matplotlib.")

    plt.figure()
    for x_vals, y_vals, label in y_series:
        plt.plot(x_vals, y_vals, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    show_plot()


def show_plot():
    """Show plots when possible, otherwise close them cleanly."""
    if plt is None:
        return

    if "agg" in plt.get_backend().lower():
        plt.close()
        return

    plt.show()


def run_convergence_study(accel_func):
    """Measure how max error changes as timestep size changes."""
    dt_list = np.array([0.2, 0.1, 0.05, 0.025, 0.0125], dtype=float)
    max_err_rk = []
    max_err_eu = []

    dt_ref_sweep = max(1e-4, float(np.min(dt_list)) / 50.0)
    t_ref, x_ref, y_ref, _, _ = simulate_with_dt(
        accel_func,
        rk4_step,
        dt_ref_sweep,
        t_max,
        stop_at_ground=False,
    )

    for dti in dt_list:
        t_rk, x_rk, y_rk, _, _ = simulate_with_dt(
            accel_func,
            rk4_step,
            float(dti),
            t_max,
            stop_at_ground=False,
        )
        t_eu, x_eu, y_eu, _, _ = simulate_with_dt(
            accel_func,
            euler_step,
            float(dti),
            t_max,
            stop_at_ground=False,
        )

        _, err_rk = position_error_vs_time(t_rk, x_rk, y_rk, t_ref, x_ref, y_ref)
        _, err_eu = position_error_vs_time(t_eu, x_eu, y_eu, t_ref, x_ref, y_ref)

        max_err_rk.append(float(np.max(err_rk)) if len(err_rk) else np.nan)
        max_err_eu.append(float(np.max(err_eu)) if len(err_eu) else np.nan)

    return dt_list, np.array(max_err_rk, dtype=float), np.array(max_err_eu, dtype=float)


def chi_squared_from_error(err_vals):
    """Return a simple chi-squared style score from position error samples."""
    err_arr = np.asarray(err_vals, dtype=float)
    return float(np.sum(err_arr**2))


def run_reference_chi_squared_study(
    accel_func,
    reference_dt=1e-4,
    *,
    dt_list=None,
    stop_at_ground=True,
):
    """Compare Euler and RK4 against a fine-step RK4 reference."""
    if dt_list is None:
        dt_list = np.array([0.2, 0.1, 0.05, 0.025, 0.0125], dtype=float)
    else:
        dt_list = np.asarray(dt_list, dtype=float)

    chi_sq_rk = []
    chi_sq_eu = []

    t_ref, x_ref, y_ref, _, _ = simulate_with_dt(
        accel_func,
        rk4_step,
        float(reference_dt),
        t_max,
        stop_at_ground=stop_at_ground,
    )

    for dti in dt_list:
        t_rk, x_rk, y_rk, _, _ = simulate_with_dt(
            accel_func,
            rk4_step,
            float(dti),
            t_max,
            stop_at_ground=stop_at_ground,
        )
        t_eu, x_eu, y_eu, _, _ = simulate_with_dt(
            accel_func,
            euler_step,
            float(dti),
            t_max,
            stop_at_ground=stop_at_ground,
        )

        _, err_rk = position_error_vs_time(t_rk, x_rk, y_rk, t_ref, x_ref, y_ref)
        _, err_eu = position_error_vs_time(t_eu, x_eu, y_eu, t_ref, x_ref, y_ref)

        chi_sq_rk.append(chi_squared_from_error(err_rk))
        chi_sq_eu.append(chi_squared_from_error(err_eu))

    return dt_list, np.array(chi_sq_rk, dtype=float), np.array(chi_sq_eu, dtype=float)


def estimate_slope(x_vals, y_vals):
    """Estimate the log-log slope for positive finite values."""
    mask = np.isfinite(y_vals) & (y_vals > 0)
    slope, _ = np.polyfit(np.log(x_vals[mask]), np.log(y_vals[mask]), 1)
    return slope


def run_simulation():
    """Run the full comparison, plots, and animation."""
    global LAST_RESULTS

    t_rk, x_rk, y_rk, vx_rk, vy_rk = simulate(acceleration_with_drag, rk4_step)
    t_eu, x_eu, y_eu, vx_eu, vy_eu = simulate(acceleration_with_drag, euler_step)

    has_analytical = not use_quadratic_drag
    analytical_results = None

    print("Integrator comparison (same settings)")
    print_summary("RK4", summarize(t_rk, x_rk, y_rk))
    print_summary("Euler", summarize(t_eu, x_eu, y_eu))

    if has_analytical:
        analytical_results = analytical_closed_form(dt)
        t_an, x_an, y_an, vx_an, vy_an = analytical_results
        print_summary("Analytical", summarize(t_an, x_an, y_an))

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
        t_an, x_an, y_an, vx_an, vy_an = analytical_results
        analytical_label = "Analytical (closed-form)"
        trajectory_series.append((x_an, y_an, analytical_label))
        speed_series.append((t_an, np.hypot(vx_an, vy_an), analytical_label))
        height_series.append((t_an, y_an, analytical_label))

    title_suffix = " vs Analytical" if has_analytical else ""
    plot_series(
        trajectory_series,
        "x (m)",
        "y (m)",
        f"Projectile Trajectory (RK4 vs Euler{title_suffix})",
    )
    plot_series(
        speed_series,
        "time (s)",
        "speed (m/s)",
        f"Speed vs Time (RK4 vs Euler{title_suffix})",
    )
    plot_series(
        height_series,
        "time (s)",
        "height y (m)",
        f"Height vs Time (RK4 vs Euler{title_suffix})",
    )

    if has_analytical:
        t_rk_err, err_rk = analytical_position_error_vs_time(t_rk, x_rk, y_rk)
        t_eu_err, err_eu = analytical_position_error_vs_time(t_eu, x_eu, y_eu)
        error_title = "Error vs Time (relative to analytical solution)"
    else:
        dt_ref = max(1e-4, dt / 50.0)
        t_ref, x_ref, y_ref, _, _ = simulate_with_dt(
            acceleration_with_drag,
            rk4_step,
            dt_ref,
            t_max,
            stop_at_ground=True,
        )

        t_rk_err, err_rk = position_error_vs_time(t_rk, x_rk, y_rk, t_ref, x_ref, y_ref)
        t_eu_err, err_eu = position_error_vs_time(t_eu, x_eu, y_eu, t_ref, x_ref, y_ref)
        error_title = "Error vs Time (relative to high-resolution RK4 reference)"

    plot_series(
        [
            (t_rk_err, err_rk, "RK4 error vs reference"),
            (t_eu_err, err_eu, "Euler error vs reference"),
        ],
        "time (s)",
        "position error (m)",
        error_title,
    )

    dt_list, max_err_rk, max_err_eu = run_convergence_study(acceleration_with_drag)
    if plt is None:
        raise RuntimeError("Convergence plotting requires matplotlib.")
    plt.figure()
    plt.loglog(dt_list, max_err_rk, marker="o", label="RK4 max error")
    plt.loglog(dt_list, max_err_eu, marker="o", label="Euler max error")
    plt.xlabel("timestep dt (s)")
    plt.ylabel("max position error over time (m)")
    plt.title("Error vs Timestep Size (log-log)")
    plt.legend()
    plt.grid(True, which="both")
    show_plot()

    print("\nEstimated convergence order from log-log slope:")
    print(f"RK4 slope   ≈ {estimate_slope(dt_list, max_err_rk):.3f}")
    print(f"Euler slope ≈ {estimate_slope(dt_list, max_err_eu):.3f}")

    if use_quadratic_drag:
        dt_chi, chi_sq_rk, chi_sq_eu = run_reference_chi_squared_study(
            acceleration_with_drag,
            reference_dt=1e-4,
            stop_at_ground=True,
        )
        plt.figure()
        plt.loglog(dt_chi, chi_sq_rk, marker="o", label="RK4 chi-squared")
        plt.loglog(dt_chi, chi_sq_eu, marker="o", label="Euler chi-squared")
        plt.xlabel("timestep dt (s)")
        plt.ylabel("chi-squared")
        plt.title("Chi-Squared vs Timestep Size (relative to RK4 dt = 0.0001)")
        plt.legend()
        plt.grid(True, which="both")
        show_plot()

        print("\nEstimated chi-squared slope from log-log fit:")
        print(f"RK4 chi-squared slope   ≈ {estimate_slope(dt_chi, chi_sq_rk):.3f}")
        print(f"Euler chi-squared slope ≈ {estimate_slope(dt_chi, chi_sq_eu):.3f}")

    if has_analytical and analytical_results is not None:
        t_an, x_an, y_an, vx_an, vy_an = analytical_results
        _, err_rk_vs_an = position_error_vs_time(t_rk, x_rk, y_rk, t_an, x_an, y_an)
        _, err_eu_vs_an = position_error_vs_time(t_eu, x_eu, y_eu, t_an, x_an, y_an)

        max_rk_an = float(np.max(err_rk_vs_an)) if len(err_rk_vs_an) else float("nan")
        max_eu_an = float(np.max(err_eu_vs_an)) if len(err_eu_vs_an) else float("nan")
        range_rk_an = float(abs(x_rk[-1] - x_an[-1]))
        range_eu_an = float(abs(x_eu[-1] - x_an[-1]))

        print("\nDistance from Analytical (closed-form) curve:")
        print(
            "RK4:   max position difference over time = "
            f"{max_rk_an:.6g} m | landing-range difference = {range_rk_an:.6g} m"
        )
        print(
            "Euler: max position difference over time = "
            f"{max_eu_an:.6g} m | landing-range difference = {range_eu_an:.6g} m"
        )

    animation_series = [
        (t_rk, x_rk, y_rk, "RK4"),
        (t_eu, x_eu, y_eu, "Euler"),
    ]
    animation_title = "RK4 vs Euler"

    display(build_animation(animation_series, animation_title))

    LAST_RESULTS = {
        "rk4": (t_rk, x_rk, y_rk, vx_rk, vy_rk),
        "euler": (t_eu, x_eu, y_eu, vx_eu, vy_eu),
    }
    if has_analytical and analytical_results is not None:
        LAST_RESULTS["analytical"] = analytical_results

    return LAST_RESULTS


if __name__ == "__main__":
    run_simulation()
