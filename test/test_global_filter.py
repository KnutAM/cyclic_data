import numpy as np
from pytest import approx

import cyclic_data.global_filter as gflt


def test_optim():
    num_points = 100
    cycle_time = np.array([0.0, 3.4, 8.2, 10.0])
    delta_ct = [0.3, -0.4]
    time = np.linspace(cycle_time[0], cycle_time[-1], num_points)
    linear_data = np.zeros(time.size)
    k_scale = 1.0
    k_factor = 1.0
    for ct in cycle_time:
        inds = time >= ct
        t_shift = time[inds] - ct
        linear_data[inds] += k_factor * k_scale * t_shift
        k_scale = 2.0
        k_factor *= -1

    test_data = {'time': time, 'lin': linear_data + 1.0e-2*(2*np.random.rand(num_points) - 1)}

    # Verify that optimization of cycle times work. Note that there is a small chance of it not
    # working due to the random pertubation. But for 0.025 this did not occur when testing 10^4 times
    cycle_time_disturb = np.copy(cycle_time)
    cycle_time_disturb[1] += delta_ct[0]
    cycle_time_disturb[2] += delta_ct[1]
    cycle_time_optim = gflt.optimize_cycle_times(test_data, cycle_time_disturb, keys=['lin'])

    assert cycle_time_optim == approx(cycle_time, abs=0.01)


def test_filter():
    num_points = 100
    cycle_time = np.array([0.0, 3.4, 8.2, 10.0])
    time = np.linspace(cycle_time[0], cycle_time[-1], num_points)
    cmat = np.random.rand(len(cycle_time)-1, 2)
    linear_data = np.zeros(num_points)
    quad_data = np.zeros(num_points)
    for ct, p in zip(cycle_time, cmat):
        inds = time >= ct
        t_shift = time[inds] - ct
        linear_data[inds] += p[0] * t_shift
        quad_data[inds] += p[0] * t_shift + p[1] * t_shift**2

    test_data = {'time': time,
                 'vals': np.random.rand(num_points),
                 'val2': np.random.rand(num_points),
                 'lin': linear_data,
                 'quad': quad_data}

    # Verify that quadratic and linear data remain unmodified when they should
    td_linear_flt = gflt.smooth_data(test_data, cycle_time, knots=3, knot_order=1, cycle_order=1,
                                     keys=['lin', 'quad', 'vals'])
    td_quad_flt = gflt.smooth_data(test_data, cycle_time, knot_order=2, cycle_order=1)

    for key in ['time', 'lin', 'val2']:
        assert td_linear_flt[key] == approx(test_data[key])

    assert not td_linear_flt['vals'] == approx(test_data['vals'])

    assert td_quad_flt['quad'] == approx(test_data['quad'])


def test_macaulay():
    test_t = np.random.rand(10)-0.5
    mac_t = gflt._macaulay(test_t)
    assert all(mac_t >= 0.0)
    assert approx(mac_t[test_t < 0]) == 0.0
    assert approx(mac_t[test_t > 0]) == test_t[test_t > 0]


# Test the update during optimization
def test_update_mat():
    a = [1.0, -1.0, 0.1]
    b = [-0.5, 0.5, 1.0]
    num_points = len(a)
    dt_change = 0.1
    dt_max = 1.0
    # Must ensure that dt_mat[0,0] is close enough to correct quad solution (0.25)
    dt_mat = np.array([[0.2/dt_change, 0.2, 0.1],
                       [0.0, 0.1, 0.4],
                       [0.1, 0.3, 0.2],
                       [0.4, 0.0, 0.3]])*dt_change

    fe_mat = np.zeros((4, num_points))
    dt0 = np.zeros(num_points)
    for i in range(dt_mat.shape[1]):
        fe_mat[:, i] = a[i] * dt_mat[:, i] ** 2 + b[i] * dt_mat[:, i]
        dt0[i] = -b[i] / (2 * a[i])

    # Constant update by dt_change
    dt_mat_cp0 = np.copy(dt_mat)
    fe_mat_cp0 = np.copy(fe_mat)
    gflt._update_mat(dt_mat_cp0, fe_mat_cp0, dt_change, dt_max, n_iter=0)
    assert dt_mat_cp0[0, :] == approx(dt_mat[0, :] + dt_change)
    for i in range(1, 4):
        assert dt_mat_cp0[i, :] == approx(dt_mat[i-1, :])

    # Update in gradient direction by dt_change
    dt_mat_cp1 = np.copy(dt_mat)
    fe_mat_cp1 = np.copy(fe_mat)
    fe_grad = (fe_mat[0, :] - fe_mat[1, :]) / (dt_mat[0, :] - dt_mat[1, :])
    gflt._update_mat(dt_mat_cp1, fe_mat_cp1, dt_change, dt_max, n_iter=1)
    assert np.sign(dt_mat_cp1[0, :] - dt_mat[0, :]) == approx(-np.sign(fe_grad))
    assert np.abs(dt_mat_cp1[0, fe_grad > 0] - dt_mat[0, fe_grad > 0]) == approx(abs(2 * dt_change))
    assert np.abs(dt_mat_cp1[0, fe_grad < 0] - dt_mat[0, fe_grad < 0]) == approx(abs(dt_change))

    # Update by quadratic approximation
    dt_mat_cp2 = np.copy(dt_mat)
    fe_mat_cp2 = np.copy(fe_mat)
    gflt._update_mat(dt_mat_cp2, fe_mat_cp2, dt_change, dt_max, n_iter=2)
    assert dt_mat_cp2[0, 0] == approx(dt0[0])   # Check quadratic update (a=1,b=-0.5)
    # Gradient update for either concave (a=-1) or too large change (a=0.1, b=1.0)
    assert approx(dt_mat_cp2[0, 1:]-dt_mat[0, 1:]) == np.sign(-fe_grad[1:])*dt_change


if __name__ == '__main__':
    test_optim()