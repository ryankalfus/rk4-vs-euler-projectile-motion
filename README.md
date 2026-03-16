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
- [`images/`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/images): saved example plots and animation screenshots
- [`ryan-professor-02-17-2026.md`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/ryan-professor-02-17-2026.md): notes/transcript from a project discussion

## Requirements

- Python 3
- NumPy
- Matplotlib
- IPython

Install the packages with:

```bash
pip install numpy matplotlib ipython
```

## How to run it

You can run the script from this folder:

```bash
python projectile-motion-simulation.py
```

You can also run it in Jupyter if you want the animation embedded in a notebook.

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
