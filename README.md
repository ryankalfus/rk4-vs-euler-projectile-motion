# Projectile Motion

This project compares `Euler` and `RK4` for 2D projectile motion.

It includes:

- a local Dash app with sliders, plots, and animation
- a public Vercel version
- the original Python simulation script
- a notebook version for Jupyter

## Live site

Public app:

- [rk4-vs-euler-projectile-motion.vercel.app](https://rk4-vs-euler-projectile-motion.vercel.app)

Vercel project:

- [vercel.com/ryansamuelkalfus-2592s-projects/rk4-vs-euler-projectile-motion](https://vercel.com/ryansamuelkalfus-2592s-projects/rk4-vs-euler-projectile-motion)

## Main files

- [`dash_app.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/dash_app.py): main interactive app
- [`projectile-motion-simulation.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/projectile-motion-simulation.py): core simulation math and original plotting/animation code
- [`simulation-notebook.ipynb`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/simulation-notebook.ipynb): notebook version
- [`api/index.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/api/index.py): Vercel Python entrypoint
- [`vercel.json`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/vercel.json): Vercel routing config

## What the app shows

- projectile trajectory
- speed vs time
- height vs time
- convergence plot: max error vs timestep size
- animation comparing `RK4` and `Euler`

When air resistance is off, it also shows distance from the analytical solution.

## Local run

Install the app dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the Dash app:

```bash
python3 dash_app.py
```

Then open:

```text
http://127.0.0.1:8050
```

## Optional notebook / script extras

If you also want to run the original script or notebook with Matplotlib plots and notebook animation, install:

```bash
python3 -m pip install matplotlib ipython notebook
```

Run the script:

```bash
python3 projectile-motion-simulation.py
```

Or open Jupyter:

```bash
jupyter notebook
```

## Physics settings

You can change:

- launch angle
- initial speed
- initial height
- timestep `dt`
- drag coefficient
- max simulation time
- air resistance on/off

## Notes

- `Euler` should be less accurate than `RK4`, especially at larger timesteps.
- On the log-log convergence plot, `Euler` should be near first-order and `RK4` should be near fourth-order.
- The deployed Vercel app uses the Dash version, not the old Streamlit version.
