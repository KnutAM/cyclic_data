import patsy
import statsmodels.api as sm


def b_spline(t, v, knot_fraction=0.5, num_knots=None, params=()):
    return spline(t, v, patsy.bs, knot_fraction, num_knots, params)


def natural_spline(t, v, knot_fraction=0.5, num_knots=None, params=()):
    return spline(t, v, patsy.cr, knot_fraction, num_knots, params)


def cubic_spline(t, v, knot_fraction=0.5, num_knots=None, params=()):
    return spline(t, v, patsy.cc, knot_fraction, num_knots, params)


def spline(t, v, spline_basis, knot_fraction=0.5, num_knots=None, params={}):
    # Setup basis function
    if 'df' in params:
        base_function = spline_basis(t, **params)
    else:
        df = int(len(t) * knot_fraction) if num_knots is None else num_knots
        base_function = spline_basis(t, df=df, **params)

    model = patsy.dmatrix(base_function, return_type='dataframe')
    fit = sm.GLM(v, model).fit()

    return fit.predict(model)
