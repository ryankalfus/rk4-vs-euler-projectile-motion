# RK4 vs Euler Projectile Motion

This project compares two numerical methods for 2D projectile motion:

- `Euler`
- `RK4` (fourth-order Runge-Kutta)

It can run in two physics modes:

- `use_quadratic_drag = True`: projectile motion with air resistance
- `use_quadratic_drag = False`: projectile motion without drag, plus an exact analytical reference

## What the script does

The main script is [`projectile-motion-simulation.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/projectile-motion-simulation.py). It:

- simulates the projectile with Euler and RK4
- plots trajectory, speed, and height
- compares error over time against a high-resolution RK4 reference
- makes a log-log convergence plot of max error vs timestep size
- shows an animation overlay of the trajectories

When drag is off, it also compares both numerical methods to the closed-form solution.

## Project files

- [`projectile-motion-simulation.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/projectile-motion-simulation.py): main simulation and plotting code
- [`simulation-notebook.ipynb`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/simulation-notebook.ipynb): easiest way to run the simulation and view plots inline in Jupyter
- [`streamlit_app.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/streamlit_app.py): interactive browser app with sliders and plots
- [`images/`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/images): saved example plots and animation screenshots
- [`ryan-professor-02-17-2026.md`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/ryan-professor-02-17-2026.md): notes/transcript from a project discussion

## Requirements

- Python 3
- NumPy
- Matplotlib
- IPython
- Streamlit

Install the packages with:

```bash
pip install numpy matplotlib ipython streamlit
```

## How to run it

### Faster browser app: Dash

If Streamlit feels laggy, run the Dash app instead:

```bash
./.venv/bin/python dash_app.py
```

Then open `http://localhost:8050`.

### Most interactive option: run the browser app

If you want sliders and a clean browser view, run:

```bash
streamlit run streamlit_app.py
```

The app lets you change:

- launch angle
- initial speed
- initial height
- timestep size
- max simulation time
- air resistance on/off

It shows:

- summary numbers
- trajectory plot
- speed plot
- height plot
- error plot
- convergence plot
- animation

You can run the script from this folder:

```bash
python projectile-motion-simulation.py
```

You can also run it in Jupyter if you want the animation embedded in a notebook.

### Cleaner option: run the notebook

If you want the outputs in one place, open the notebook:

```bash
python3 -m pip install notebook numpy matplotlib ipython
jupyter notebook
```

Then open [`simulation-notebook.ipynb`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/simulation-notebook.ipynb) and run the code cell.

## Settings you can change

Near the top of the script, you can adjust:

- `theta_deg`
- `v0`
- `y0`
- `dt`
- `t_max`
- `use_quadratic_drag`

## Reading the results

- Euler is expected to be less accurate, especially for larger timestep sizes.
- RK4 is expected to stay much closer to the reference solution.
- On the log-log error plot, Euler should look close to first-order and RK4 should look close to fourth-order.

## Notes

- The analytical solution only appears when drag is off.
- Some RK4 and analytical curves may overlap so closely that they look like one line.
