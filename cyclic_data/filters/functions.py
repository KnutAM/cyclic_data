import numpy as np
import patsy
import statsmodels.api as sm


def polynomial(t, v, deg=3, t_pred=None):
    """ Smooth v-data using polynomial of given degree
    """
    p = np.polyfit(t, v, deg=deg)
    if t_pred is None:
        return np.polyval(p, t)
    else:
        return np.polyval(p, t_pred)


def linear_segments(t, v, num_segments=20, t_pred=None):
    """ Smooth v-data by fitting num_segments equally spaced linear segments
    """
    assert len(t) > num_segments, 'number of segments cannot be more than number of datapoints'
    return spline(t, v, patsy.bs, num_knots=num_segments, b_degree=1, t_pred=t_pred)


def b_spline(t, v, knot_fraction=0.25, num_knots=None, t_pred=None):
    """ Smooth v-data using B-spline
    """
    return spline(t, v, patsy.bs, knot_fraction, num_knots, t_pred=t_pred)


def natural_spline(t, v, knot_fraction=0.25, num_knots=None, t_pred=None):
    """ Smooth v-data using a natural cubic spline
    """
    return spline(t, v, patsy.cr, knot_fraction, num_knots, t_pred=t_pred)


def cubic_spline(t, v, knot_fraction=0.25, num_knots=None, t_pred=None):
    """ Smooth v-data using a cubic spline
    """
    return spline(t, v, patsy.cc, knot_fraction, num_knots, t_pred=t_pred)


def spline(t, v, spline_basis, knot_fraction=0.25, num_knots=None, b_degree=None, t_pred=None):
    """ Smooth using a given spline basis with num_knots
    If num_knots not given, set num_knots = floor(len(t)*knot_fraction)
    If t_pred given, return predicted values for different time coordinates
    """
    # Set parameters if b_degree given (degree of b-spline)
    params = {} if b_degree is None else {'degree': b_degree}

    # Setup basis function, need to define knots and bounds explicitly for prediction to work correctly
    # (I.e. we need to use the same knots for prediction as for fitting!)
    # Get number of knots
    num_knots_ = int(len(t) * knot_fraction) if num_knots is None else num_knots
    # Distribute knots
    knots = tuple(np.linspace(t[0], t[-1], num_knots_))
    # Find bounds
    t_min = np.min(t) if t_pred is None else min(np.min(t), np.min(t_pred))
    t_max = np.max(t) if t_pred is None else max(np.max(t), np.max(t_pred))
    # Expand bounds to avoid numerical issues (double precision)
    t_min -= abs(t_min) * 1.e-12 + 1.e-100
    t_max += abs(t_max) * 1.e-12 + 1.e-100

    # Construct base function for fitting
    base_function = spline_basis(t, knots=knots, lower_bound=t_min, upper_bound=t_max, **params)

    # Construct model for fitting
    model = patsy.dmatrix(base_function)

    # Fit model
    fit = sm.GLM(v, model).fit()

    if t_pred is None:  # Return smoothened values by evaluating the model at the fitted data
        smoothened = fit.predict(model)
    else:               # Use the fit to predict new time values
        pred_base = spline_basis(t_pred, knots=knots, lower_bound=t_min, upper_bound=t_max, **params)
        pred_model = patsy.dmatrix(pred_base)
        smoothened = fit.predict(pred_model)

    return np.array(smoothened)