import numpy as np
from pytest import approx

import cyclic_data.filter as flt


def assert_dict_equality(dict1, dict2):
    for key in dict1:
        assert key in dict2
        assert dict1[key] == approx(dict2[key])


def test_smoothen():
    num_points = 100
    test_data = {'time': np.linspace(0, 10),
                 'vals': np.random.rand(num_points),
                 'val2': np.random.rand(num_points)}
    pv_inds = [[3, 40, 80],
               [6, 43, 90]]

    def dummy_filter(_, v):
        return v

    def filter_2(_, v):
        return v

    assert_dict_equality(flt.smoothen(test_data, pv_inds, dummy_filter),
                         test_data)

    assert_dict_equality(flt.smoothen(test_data, pv_inds, dummy_filter, keys=['vals']),
                         test_data)

    flt_dict = {'vals': dummy_filter, 'val2': filter_2}
    assert_dict_equality(flt.smoothen(test_data, pv_inds, flt_dict),
                         test_data)


def test_filters():
    num_points = 100
    t = np.linspace(0, 10, num_points)
    v = np.random.rand(num_points) + 2*t + 0.02*t**3
    v_lin = 2 + 3*t
    filter_functions = [flt.polynomial, flt.linear_segments, flt.cubic_spline]
    for fun in filter_functions:
        # Test that returned length is the same
        vf = fun(t, v)
        assert len(vf) == len(t)
        # Test that the predicted returned values are the same as the filtered
        # if the time input is the same
        vp = fun(t, v, t_pred=t)
        assert vp == approx(vf)
        # Test that linear input is not modified
        vp_lin = fun(t, v_lin)
        assert vp_lin == approx(v_lin)

    # Test that quadratic function is represented exactly when it should
    v_quad = 3 + 2 * t + t ** 2
    assert flt.polynomial(t, v_quad, deg=2) == approx(v_quad)
    assert flt.cubic_spline(t, v_quad) == approx(v_quad)

    # Test that cubic function is represented exactly when it should
    v_cube = v_quad + 3.1 * t ** 3
    assert flt.cubic_spline(t, v_cube, num_knots=3) == approx(v_cube)


