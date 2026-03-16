import importlib.util
import pathlib
import unittest

import numpy as np


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "projectile-motion-simulation.py"
SPEC = importlib.util.spec_from_file_location("projectile_motion_simulation", MODULE_PATH)
SIM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SIM)


class ProjectileMotionTests(unittest.TestCase):
    def setUp(self):
        self.original_values = {
            "theta_deg": SIM.theta_deg,
            "v0": SIM.v0,
            "y0": SIM.y0,
            "dt": SIM.dt,
            "t_max": SIM.t_max,
            "use_quadratic_drag": SIM.use_quadratic_drag,
        }

    def tearDown(self):
        for name, value in self.original_values.items():
            setattr(SIM, name, value)

    def test_no_drag_acceleration_is_gravity_only(self):
        SIM.use_quadratic_drag = False

        ax, ay = SIM.acceleration_with_drag(3.0, 4.0)

        self.assertAlmostEqual(ax, 0.0)
        self.assertAlmostEqual(ay, -SIM.g)

    def test_rk4_is_more_accurate_than_euler_without_drag(self):
        SIM.use_quadratic_drag = False
        SIM.dt = 0.2
        SIM.t_max = 3.0

        t_rk, x_rk, y_rk, _, _ = SIM.simulate(SIM.acceleration_with_drag, SIM.rk4_step)
        t_eu, x_eu, y_eu, _, _ = SIM.simulate(SIM.acceleration_with_drag, SIM.euler_step)
        t_an, x_an, y_an, _, _ = SIM.analytical_closed_form(SIM.dt)

        _, err_rk = SIM.position_error_vs_time(t_rk, x_rk, y_rk, t_an, x_an, y_an)
        _, err_eu = SIM.position_error_vs_time(t_eu, x_eu, y_eu, t_an, x_an, y_an)

        self.assertLess(float(np.max(err_rk)), float(np.max(err_eu)))

    def test_time_format_uses_minutes_seconds_and_hundredths(self):
        self.assertEqual(SIM.format_mm_ss_hh(61.23), "01:01.23")


if __name__ == "__main__":
    unittest.main()
