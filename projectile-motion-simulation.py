# --- imports ---
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, clear_output, HTML
from matplotlib.animation import FuncAnimation

# ----------------------------
# Projectile Motion Simulator
# Air resistance always ON (set by user)
# Compare integrators: RK4 vs Euler
# + 2D ball animation overlay with time overlay (mm:ss.hh)
# ----------------------------

# ---- Parameters you can change ----
g = 9.81                    # m/s^2
theta_deg = 45              # launch angle in degrees
v0 = 20.0                   # initial speed (m/s)
y0 = 0.0                    # initial height (m)

# Drag options:
use_quadratic_drag = True   # True: quadratic drag, False: NO drag

# Physical-ish defaults (good enough for a project)
m = 0.145                   # mass (kg) ~ baseball
rho = 1.225                 # air density (kg/m^3)
Cd = 0.47                   # drag coefficient (~sphere)
r = 0.0366                  # radius (m) ~ baseball
A = np.pi * r**2            # cross-sectional area (m^2)

# Quadratic drag coefficient: a_drag = -(k/m)*|v|*v
k_quad = 0.5 * rho * Cd * A

# Linear drag coefficient (deprecated in this version; kept for compatibility)
b_lin = 0.02                # kg/s (not used in this version)

# Enforce: if no quadratic drag, then no drag at all and b_lin = 0
if not use_quadratic_drag:
    b_lin = 0.0

dt = 0.1                    # time step (s)
t_max = 10.0                # max sim time (s)

# ---- Helper functions ----
def acceleration_with_drag(vx, vy):
    if use_quadratic_drag:
        v = np.hypot(vx, vy)
        ax = -(k_quad / m) * v * vx
        ay = -g - (k_quad / m) * v * vy
    else:
        # NO drag
        ax = 0.0
        ay = -g
    return ax, ay

# ---- Integrators ----
def euler_step(state, dt, accel_func):
    x, y, vx, vy = state
    ax, ay = accel_func(vx, vy)

    x_new  = x  + dt * vx
    y_new  = y  + dt * vy
    vx_new = vx + dt * ax
    vy_new = vy + dt * ay

    return np.array([x_new, y_new, vx_new, vy_new], dtype=float)

def rk4_step(state, dt, accel_func):
    def f(s):
        x, y, vx, vy = s
        ax, ay = accel_func(vx, vy)
        return np.array([vx, vy, ax, ay], dtype=float)

    k1 = f(state)
    k2 = f(state + 0.5 * dt * k1)
    k3 = f(state + 0.5 * dt * k2)
    k4 = f(state + dt * k3)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

# ---- Simulator ----
def simulate(accel_func, step_func):
    theta = np.deg2rad(theta_deg)
    vx0 = v0 * np.cos(theta)
    vy0 = v0 * np.sin(theta)

    state = np.array([0.0, y0, vx0, vy0], dtype=float)

    t_vals = [0.0]
    x_vals = [state[0]]
    y_vals = [state[1]]
    vx_vals = [state[2]]
    vy_vals = [state[3]]

    t = 0.0
    for _ in range(int(t_max / dt)):
        state = step_func(state, dt, accel_func)
        t += dt

        if state[1] < 0 and t > dt:
            x_prev, y_prev = x_vals[-1], y_vals[-1]
            x_new, y_new = state[0], state[1]
            denom = (y_prev - y_new)
            frac = (y_prev / denom) if denom != 0 else 1.0

            x_land = x_prev + frac * (x_new - x_prev)
            t_land = t_vals[-1] + frac * (t - t_vals[-1])

            t_vals.append(t_land)
            x_vals.append(x_land)
            y_vals.append(0.0)
            vx_vals.append(state[2])
            vy_vals.append(state[3])
            break

        t_vals.append(t)
        x_vals.append(state[0])
        y_vals.append(state[1])
        vx_vals.append(state[2])
        vy_vals.append(state[3])

    return (np.array(t_vals), np.array(x_vals), np.array(y_vals),
            np.array(vx_vals), np.array(vy_vals))

# ---- Simulator that accepts dt/t_max (for timestep-size error study) ----
# NOTE: stop_at_ground=False is used for convergence-order plots so the ground-impact
#       event doesn’t dominate/cap the apparent order.
def simulate_with_dt(accel_func, step_func, dt_local, t_max_local, stop_at_ground=True):
    theta = np.deg2rad(theta_deg)
    vx0 = v0 * np.cos(theta)
    vy0 = v0 * np.sin(theta)

    state = np.array([0.0, y0, vx0, vy0], dtype=float)

    t_vals = [0.0]
    x_vals = [state[0]]
    y_vals = [state[1]]
    vx_vals = [state[2]]
    vy_vals = [state[3]]

    t = 0.0
    for _ in range(int(t_max_local / dt_local)):
        state = step_func(state, dt_local, accel_func)
        t += dt_local

        if stop_at_ground and (state[1] < 0) and (t > dt_local):
            x_prev, y_prev = x_vals[-1], y_vals[-1]
            x_new, y_new = state[0], state[1]
            denom = (y_prev - y_new)
            frac = (y_prev / denom) if denom != 0 else 1.0

            x_land = x_prev + frac * (x_new - x_prev)
            t_land = t_vals[-1] + frac * (t - t_vals[-1])

            t_vals.append(t_land)
            x_vals.append(x_land)
            y_vals.append(0.0)
            vx_vals.append(state[2])
            vy_vals.append(state[3])
            break

        t_vals.append(t)
        x_vals.append(state[0])
        y_vals.append(state[1])
        vx_vals.append(state[2])
        vy_vals.append(state[3])

    return (np.array(t_vals), np.array(x_vals), np.array(y_vals),
            np.array(vx_vals), np.array(vy_vals))

# ---- Error helpers (using a high-resolution RK4 run as "reference") ----
def position_error_vs_time(t, x, y, t_ref, x_ref, y_ref):
    t_end = min(float(t[-1]), float(t_ref[-1]))
    mask = t <= t_end
    t_use = t[mask]
    x_use = x[mask]
    y_use = y[mask]

    x_ref_i = np.interp(t_use, t_ref, x_ref)
    y_ref_i = np.interp(t_use, t_ref, y_ref)

    err = np.hypot(x_use - x_ref_i, y_use - y_ref_i)
    return t_use, err

# ---- Analytical closed-form solution (only valid for NO-drag case) ----
def analytical_closed_form(dt_local):
    theta = np.deg2rad(theta_deg)
    vx0 = v0 * np.cos(theta)
    vy0 = v0 * np.sin(theta)

    disc = vy0**2 + 2.0 * g * y0
    disc = max(0.0, float(disc))
    t_land = (vy0 + np.sqrt(disc)) / g if g != 0 else 0.0

    if t_land <= 0:
        t_vals = np.array([0.0], dtype=float)
    else:
        n = int(np.floor(t_land / dt_local))
        t_vals = np.arange(0.0, (n + 1) * dt_local + 1e-15, dt_local, dtype=float)
        if t_vals[-1] < t_land - 1e-12:
            t_vals = np.append(t_vals, t_land)
        else:
            t_vals[-1] = t_land

    x_vals = vx0 * t_vals
    y_vals = y0 + vy0 * t_vals - 0.5 * g * t_vals**2
    y_vals = np.maximum(y_vals, 0.0)

    vx_vals = np.full_like(t_vals, vx0, dtype=float)
    vy_vals = vy0 - g * t_vals

    return t_vals, x_vals, y_vals, vx_vals, vy_vals

# ---- Animation helpers ----
def format_mm_ss_hh(seconds_float):
    total_hundredths = int(round(seconds_float * 100))
    minutes = total_hundredths // (60 * 100)
    rem = total_hundredths % (60 * 100)
    secs = rem // 100
    hundredths = rem % 100
    return f"{minutes:02d}:{secs:02d}.{hundredths:02d}"

def overlay_ball_animation(t_rk, x_rk, y_rk, t_eu, x_eu, y_eu, title="RK4 vs Euler"):
    def downsample(t, x, y, target=400):
        n = len(t)
        step = max(1, n // target)
        return t[::step], x[::step], y[::step]

    tR, xR, yR = downsample(t_rk, x_rk, y_rk)
    tE, xE, yE = downsample(t_eu, x_eu, y_eu)
    frames = min(len(tR), len(tE))

    fig, ax = plt.subplots()
    ax.set_axis_off()
    ax.set_aspect("equal", adjustable="box")

    x_max = float(max(np.max(xR), np.max(xE))) if frames else 1.0
    y_max = float(max(np.max(yR), np.max(yE))) if frames else 1.0
    ax.set_xlim(-0.05 * x_max, 1.05 * x_max)
    ax.set_ylim(-0.10 * max(1.0, y_max), 1.10 * max(1.0, y_max))

    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [0, 0], linewidth=2)

    trail_rk, = ax.plot([], [], linewidth=2, alpha=0.35, label="RK4")
    trail_eu, = ax.plot([], [], linewidth=2, alpha=0.35, label="Euler")
    ball_rk, = ax.plot([], [], marker="o", markersize=14, label="RK4")
    ball_eu, = ax.plot([], [], marker="o", markersize=14, label="Euler")

    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=14, va="top")
    title_text = ax.text(0.5, 0.98, title, transform=ax.transAxes,
                         fontsize=14, va="top", ha="center")

    fig.subplots_adjust(bottom=0.14)
    legend = ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.10),
                       frameon=True, ncol=1, handlelength=2.0, borderaxespad=0.0)
    legend.set_title("Key (color → method)")

    def init():
        trail_rk.set_data([], [])
        trail_eu.set_data([], [])
        ball_rk.set_data([], [])
        ball_eu.set_data([], [])
        time_text.set_text("")
        return trail_rk, trail_eu, ball_rk, ball_eu, time_text, title_text

    def update(i):
        trail_rk.set_data(xR[:i+1], yR[:i+1])
        trail_eu.set_data(xE[:i+1], yE[:i+1])
        ball_rk.set_data([xR[i]], [yR[i]])
        ball_eu.set_data([xE[i]], [yE[i]])
        time_text.set_text(f"t = {format_mm_ss_hh(tR[i])}")
        return trail_rk, trail_eu, ball_rk, ball_eu, time_text, title_text

    ani = FuncAnimation(fig, update, frames=frames, init_func=init, interval=20, blit=True)
    plt.close(fig)
    return HTML(ani.to_jshtml())

def overlay_ball_animation_with_analytical(t_rk, x_rk, y_rk,
                                          t_eu, x_eu, y_eu,
                                          t_an, x_an, y_an,
                                          title="RK4 vs Euler vs Analytical"):
    def downsample(t, x, y, target=400):
        n = len(t)
        step = max(1, n // target)
        return t[::step], x[::step], y[::step]

    tR, xR, yR = downsample(t_rk, x_rk, y_rk)
    tE, xE, yE = downsample(t_eu, x_eu, y_eu)
    tA, xA, yA = downsample(t_an, x_an, y_an)

    frames = min(len(tR), len(tE), len(tA))

    fig, ax = plt.subplots()
    ax.set_axis_off()
    ax.set_aspect("equal", adjustable="box")

    x_max = float(max(np.max(xR), np.max(xE), np.max(xA))) if frames else 1.0
    y_max = float(max(np.max(yR), np.max(yE), np.max(yA))) if frames else 1.0
    ax.set_xlim(-0.05 * x_max, 1.05 * x_max)
    ax.set_ylim(-0.10 * max(1.0, y_max), 1.10 * max(1.0, y_max))

    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [0, 0], linewidth=2)

    trail_rk, = ax.plot([], [], linewidth=2, alpha=0.35, label="RK4")
    trail_eu, = ax.plot([], [], linewidth=2, alpha=0.35, label="Euler")
    trail_an, = ax.plot([], [], linewidth=2, alpha=0.35, label="Analytical (closed-form)")

    ball_rk, = ax.plot([], [], marker="o", markersize=14, label="RK4")
    ball_eu, = ax.plot([], [], marker="o", markersize=14, label="Euler")
    ball_an, = ax.plot([], [], marker="o", markersize=14, label="Analytical (closed-form)")

    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=14, va="top")
    title_text = ax.text(0.5, 0.98, title, transform=ax.transAxes,
                         fontsize=14, va="top", ha="center")

    fig.subplots_adjust(bottom=0.14)
    legend = ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.10),
                       frameon=True, ncol=1, handlelength=2.0, borderaxespad=0.0)
    legend.set_title("Key (color → method)")

    def init():
        trail_rk.set_data([], [])
        trail_eu.set_data([], [])
        trail_an.set_data([], [])
        ball_rk.set_data([], [])
        ball_eu.set_data([], [])
        ball_an.set_data([], [])
        time_text.set_text("")
        return (trail_rk, trail_eu, trail_an,
                ball_rk, ball_eu, ball_an,
                time_text, title_text)

    def update(i):
        trail_rk.set_data(xR[:i+1], yR[:i+1])
        trail_eu.set_data(xE[:i+1], yE[:i+1])
        trail_an.set_data(xA[:i+1], yA[:i+1])

        ball_rk.set_data([xR[i]], [yR[i]])
        ball_eu.set_data([xE[i]], [yE[i]])
        ball_an.set_data([xA[i]], [yA[i]])

        time_text.set_text(f"t = {format_mm_ss_hh(tR[i])}")
        return (trail_rk, trail_eu, trail_an,
                ball_rk, ball_eu, ball_an,
                time_text, title_text)

    ani = FuncAnimation(fig, update, frames=frames, init_func=init, interval=20, blit=True)
    plt.close(fig)
    return HTML(ani.to_jshtml())

# ==========================
# Run once: RK4 vs Euler
# ==========================

clear_output(wait=True)

t_rk, x_rk, y_rk, vx_rk, vy_rk = simulate(acceleration_with_drag, rk4_step)
t_eu, x_eu, y_eu, vx_eu, vy_eu = simulate(acceleration_with_drag, euler_step)

def summarize(t_vals, x_vals, y_vals):
    return {
        "Range (m)": float(x_vals[-1]),
        "Max height (m)": float(np.max(y_vals)),
        "Time (s)": float(t_vals[-1]),
    }

stats_rk = summarize(t_rk, x_rk, y_rk)
stats_eu = summarize(t_eu, x_eu, y_eu)

print("Integrator comparison (same settings)")
print(f"RK4:   Range: {stats_rk['Range (m)']:.2f} m | Max height: {stats_rk['Max height (m)']:.2f} m | Time: {stats_rk['Time (s)']:.2f} s")
print(f"Euler: Range: {stats_eu['Range (m)']:.2f} m | Max height: {stats_eu['Max height (m)']:.2f} m | Time: {stats_eu['Time (s)']:.2f} s")

# If NO-drag, compute analytical; if drag is on, do NOT compute/plot it
has_analytical = not use_quadratic_drag

if has_analytical:
    t_an, x_an, y_an, vx_an, vy_an = analytical_closed_form(dt)
    stats_an = summarize(t_an, x_an, y_an)
    print(f"Analytical: Range: {stats_an['Range (m)']:.2f} m | Max height: {stats_an['Max height (m)']:.2f} m | Time: {stats_an['Time (s)']:.2f} s")

# --- Trajectory plot ---
plt.figure()
plt.plot(x_rk, y_rk, label="RK4")
plt.plot(x_eu, y_eu, label="Euler")
if has_analytical:
    plt.plot(x_an, y_an, label="Analytical (closed-form)")
plt.xlabel("x (m)")
plt.ylabel("y (m)")
plt.title("Projectile Trajectory (RK4 vs Euler" + (" vs Analytical" if has_analytical else "") + ")")
plt.legend()
plt.grid(True)
plt.show()

# --- Speed vs time ---
speed_rk = np.hypot(vx_rk, vy_rk)
speed_eu = np.hypot(vx_eu, vy_eu)

plt.figure()
plt.plot(t_rk, speed_rk, label="RK4")
plt.plot(t_eu, speed_eu, label="Euler")
if has_analytical:
    speed_an = np.hypot(vx_an, vy_an)
    plt.plot(t_an, speed_an, label="Analytical (closed-form)")
plt.xlabel("time (s)")
plt.ylabel("speed (m/s)")
plt.title("Speed vs Time (RK4 vs Euler" + (" vs Analytical" if has_analytical else "") + ")")
plt.legend()
plt.grid(True)
plt.show()

# --- Height vs time ---
plt.figure()
plt.plot(t_rk, y_rk, label="RK4")
plt.plot(t_eu, y_eu, label="Euler")
if has_analytical:
    plt.plot(t_an, y_an, label="Analytical (closed-form)")
plt.xlabel("time (s)")
plt.ylabel("height y (m)")
plt.title("Height vs Time (RK4 vs Euler" + (" vs Analytical" if has_analytical else "") + ")")
plt.legend()
plt.grid(True)
plt.show()

# ==========================
# Error vs time and Error vs timestep size
# ==========================

dt_ref = max(1e-4, dt / 50.0)
t_ref, x_ref, y_ref, vx_ref, vy_ref = simulate_with_dt(
    acceleration_with_drag, rk4_step, dt_ref, t_max, stop_at_ground=True
)

t_rk_err, err_rk = position_error_vs_time(t_rk, x_rk, y_rk, t_ref, x_ref, y_ref)
t_eu_err, err_eu = position_error_vs_time(t_eu, x_eu, y_eu, t_ref, x_ref, y_ref)

plt.figure()
plt.plot(t_rk_err, err_rk, label="RK4 error vs reference")
plt.plot(t_eu_err, err_eu, label="Euler error vs reference")
plt.xlabel("time (s)")
plt.ylabel("position error (m)")
plt.title("Error vs Time (relative to high-resolution RK4 reference)")
plt.legend()
plt.grid(True)
plt.show()

# ==========================
# Convergence study (max error vs timestep)
# IMPORTANT: stop_at_ground=False so the landing event doesn't cap the order
# ==========================

dt_list = np.array([0.2, 0.1, 0.05, 0.025, 0.0125], dtype=float)

max_err_rk = []
max_err_eu = []

dt_ref_sweep = max(1e-4, float(np.min(dt_list)) / 50.0)
t_ref_s, x_ref_s, y_ref_s, vx_ref_s, vy_ref_s = simulate_with_dt(
    acceleration_with_drag, rk4_step, dt_ref_sweep, t_max, stop_at_ground=False
)

for dti in dt_list:
    t_rk_i, x_rk_i, y_rk_i, _, _ = simulate_with_dt(
        acceleration_with_drag, rk4_step, float(dti), t_max, stop_at_ground=False
    )
    t_eu_i, x_eu_i, y_eu_i, _, _ = simulate_with_dt(
        acceleration_with_drag, euler_step, float(dti), t_max, stop_at_ground=False
    )

    _, err_rk_i = position_error_vs_time(t_rk_i, x_rk_i, y_rk_i, t_ref_s, x_ref_s, y_ref_s)
    _, err_eu_i = position_error_vs_time(t_eu_i, x_eu_i, y_eu_i, t_ref_s, x_ref_s, y_ref_s)

    max_err_rk.append(float(np.max(err_rk_i)) if len(err_rk_i) else np.nan)
    max_err_eu.append(float(np.max(err_eu_i)) if len(err_eu_i) else np.nan)

max_err_rk = np.array(max_err_rk, dtype=float)
max_err_eu = np.array(max_err_eu, dtype=float)

plt.figure()
plt.loglog(dt_list, max_err_rk, marker="o", label="RK4 max error")
plt.loglog(dt_list, max_err_eu, marker="o", label="Euler max error")
plt.xlabel("timestep dt (s)")
plt.ylabel("max position error over time (m)")
plt.title("Error vs Timestep Size (log-log)")
plt.legend()
plt.grid(True, which="both")
plt.show()

# ---- Estimate convergence slopes from log-log data (MOVED HERE so arrays exist) ----
mask_rk = np.isfinite(max_err_rk) & (max_err_rk > 0)
mask_eu = np.isfinite(max_err_eu) & (max_err_eu > 0)

slope_rk, intercept_rk = np.polyfit(
    np.log(dt_list[mask_rk]),
    np.log(max_err_rk[mask_rk]),
    1
)

slope_eu, intercept_eu = np.polyfit(
    np.log(dt_list[mask_eu]),
    np.log(max_err_eu[mask_eu]),
    1
)

print("\nEstimated convergence order from log-log slope:")
print(f"RK4 slope  ≈ {slope_rk:.3f}")
print(f"Euler slope ≈ {slope_eu:.3f}")

# ==========================
# Distance to analytical (ONLY for NO-drag case)
# ==========================

if has_analytical:
    t_rk_vs_an, err_rk_vs_an = position_error_vs_time(t_rk, x_rk, y_rk, t_an, x_an, y_an)
    t_eu_vs_an, err_eu_vs_an = position_error_vs_time(t_eu, x_eu, y_eu, t_an, x_an, y_an)

    max_rk_an = float(np.max(err_rk_vs_an)) if len(err_rk_vs_an) else float("nan")
    max_eu_an = float(np.max(err_eu_vs_an)) if len(err_eu_vs_an) else float("nan")

    range_rk_an = float(abs(x_rk[-1] - x_an[-1]))
    range_eu_an = float(abs(x_eu[-1] - x_an[-1]))

    print("\nDistance from Analytical (closed-form) curve:")
    print(f"RK4:   max position difference over time = {max_rk_an:.6g} m | landing-range difference = {range_rk_an:.6g} m")
    print(f"Euler: max position difference over time = {max_eu_an:.6g} m | landing-range difference = {range_eu_an:.6g} m")

# ==========================
# Animation
# ==========================

if has_analytical:
    display(overlay_ball_animation_with_analytical(
        t_rk, x_rk, y_rk,
        t_eu, x_eu, y_eu,
        t_an, x_an, y_an,
        "RK4 vs Euler vs Analytical"
    ))
else:
    display(overlay_ball_animation(
        t_rk, x_rk, y_rk,
        t_eu, x_eu, y_eu,
        "RK4 vs Euler"
    ))

LAST_RESULTS = {
    "rk4": (t_rk, x_rk, y_rk, vx_rk, vy_rk),
    "euler": (t_eu, x_eu, y_eu, vx_eu, vy_eu),
}
if has_analytical:
    LAST_RESULTS["analytical"] = (t_an, x_an, y_an, vx_an, vy_an)
