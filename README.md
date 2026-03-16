# Projectile Motion

This project compares `Euler` and `RK4` for 2D projectile motion.

The main app is built with `Dash` and includes:

- sliders for the launch settings
- a 2D flight animation
- trajectory, speed, and height plots
- a convergence plot for timestep error
- an analytical comparison when air resistance is off

## Live Site

- Public app: [rk4-vs-euler-projectile-motion.vercel.app](https://rk4-vs-euler-projectile-motion.vercel.app)
- Vercel project: [ryansamuelkalfus-2592s-projects/rk4-vs-euler-projectile-motion](https://vercel.com/ryansamuelkalfus-2592s-projects/rk4-vs-euler-projectile-motion)

## Main Files

- [`dash_app.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/dash_app.py): interactive Dash app
- [`projectile-motion-simulation.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/projectile-motion-simulation.py): simulation math and optional notebook/plot helpers
- [`simulation-notebook.ipynb`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/simulation-notebook.ipynb): notebook version
- [`api/index.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/api/index.py): Vercel Python entrypoint
- [`vercel.json`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/vercel.json): Vercel routing config
- [`assets/app.css`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/assets/app.css): app styling

## Run Locally

Install the app dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start the app:

```bash
python3 dash_app.py
```

Then open:

```text
http://127.0.0.1:8050
```

## Optional Notebook / Script Setup

The deployed app only needs the packages in [`requirements.txt`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/requirements.txt).

If you also want to run the original script with Matplotlib plots or use the notebook, install:

```bash
python3 -m pip install matplotlib ipython notebook
```

Run the script:

```bash
python3 projectile-motion-simulation.py
```

Open Jupyter:

```bash
jupyter notebook
```

## Controls

You can change:

- launch angle
- initial speed
- initial height
- timestep `dt`
- drag coefficient
- max simulation time
- air resistance on/off

## How To Read The Results

- `Euler` is simpler but less accurate.
- `RK4` should stay much closer to the correct trajectory.
- On the log-log convergence plot, `Euler` should be close to first-order.
- On the same plot, `RK4` should be close to fourth-order.
- The analytical comparison only appears when air resistance is off.

## Deployment

This project is deployed on Vercel using:

- [`api/index.py`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/api/index.py) as the Python entrypoint
- [`vercel.json`](/Users/ryankalfus/Downloads/codex-projects/rk4-vs-euler-projectile-motion/vercel.json) for routing

To redeploy from this folder:

```bash
npx vercel deploy --prod --yes
```
