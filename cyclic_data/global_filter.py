import numpy as np


def smooth_data(data, cycle_time, keys=None, knots=10, knot_order=3, cycle_order=0, max_ind=0):
    """ Smooth data using splines

    :param data: test data - dictionary containing time series arrays
    :type data: dict[ ndarray ]
    
    :param cycle_time: List of times when the cycle changes
    :type cycle_time: Iterable[ float ]
    
    :param keys: List of items in data to smoothen. If None filter all 
                 but 'time' and 'stp'
    :type keys: list[ str ], None
    
    :param knots: A list of knot locations between 0 and 1 or the number 
                  of knots (to be uniformly distributed)
    :type knots: Iterable[ float ], int
    
    :param knot_order: The polynomial order over each knot (the 
                       derivative number - 1 to be continuous)
    :type knot_order: int
    
    :param cycle_order: The polynomial order over each cycle (the 
                        derivative number - 1to be continuous)
    :type cycle_order: int

    :return: Smoothened data. The time vector remain unaltered.

    """
    # Create a new data variable for smoothened data
    sdata = {}
    for key in data:
        sdata[key] = np.copy(data[key]) if max_ind == 0 else data[key][:max_ind]

    # Calculate the fitting matrix
    fit_matrix = get_fit_matrix(sdata['time'], cycle_time, knots, 
                                knot_order, cycle_order)

    # Decide which keys in data to fit
    if keys is None:
        _keys = [key for key in data if key not in ['time', 'stp']]
    else:
        assert all([key in data for key in keys]), ('All keys specified to \
                                                     smooth_data must be in data')
        _keys = keys[:]

    for key in _keys:
        # Fit parameters
        fit_result = np.linalg.lstsq(fit_matrix, sdata[key], rcond=None)
        coeff = fit_result[0]

        # Calculate response
        sdata[key] = fit_matrix @ coeff

    return sdata


def optimize_cycle_times(data, cycle_time, keys=None, dt_max=0.1, max_iter=100, 
                         knots=0, knot_order=1, cycle_order=1, max_ind=0):
    """ Function that optimize the cycle time points, to reduce the fitting
    error. It supports accounting for multiple channels, but in general 
    it can be best to choose the controlled channel(s) and the default
    linear interpolations within each channel. This assumes that the 
    control is linear within each cycle (e.g. triangular loading)
    
    :param data: The test data for which the cycle times should be optimized
    :type data: dict[ np.array ]
    
    :param cycle_time: Initial values for the cycle time
    :type cycle_time: np.array
    
    :param keys: List of items in data that should be used when optimizing
                 cycle times. 
    :type keys: list[ str ]
    
    :param dt_max: max change of cycle time
    
    :param max_iter: maximum number of optimization iterations
    
    For description of ``knots``, ``knot_order`` and ``cycle_order``, 
    see :py:func:`smooth_data`.
    
    """
    def scale_fun(t):
        return def_scale_fun(t, t5=dt_max*3)

    objective_function = get_objfun(data, keys, knots, knot_order, 
                                    cycle_order, scale_fun=scale_fun, max_ind=max_ind)

    opt_cycle_time = minimize(objective_function, cycle_time,
                              dt_init=dt_max/10, dt_max=dt_max, 
                              dt_change_tol=dt_max/1000, max_iter=max_iter)

    return opt_cycle_time


def get_fit_matrix(time, cycle_times, knots=10, knot_order=3, cycle_order=0):
    """ Return the matrix that allows fitting of the following function:

    .. math::
        f(t) = \\sum_{j=0}^{N_\\mathrm{co}-1} k_j 
        \\left[\\frac{t-t_0}{t_\\mathrm{end}-t_0}\\right]^j +
        \\sum_{i=1}^{N_\\mathrm{c}} 
        \\left[ \\sum_{j=N_\\mathrm{co}}^{N_\\mathrm{ko}}\\left[p_{ij}T_i(t)^{j}\\right] +
        \\sum_{k=1}^{N_\\mathrm{k}}\\left[q_{ik}h_{ik}(t)^{N_\\mathrm{ko}}\\right] \\right]

    where :math:`N_\\mathrm{co}` is ``
    """
    assert knot_order >= cycle_order

    if isinstance(knots, int):
        t_knots = np.linspace(0, 1, knots+2)[1:-1]  # Make knots uniformly distributed, but remove ends
    else:
        t_knots = np.array(knots)

    num_cycles = len(cycle_times) - 1
    num_params = cycle_order + num_cycles * (1 + knot_order - cycle_order + len(t_knots))
    fit_matrix = np.zeros((len(time), num_params))

    # Apply fixed polynomial part
    f_col = 0
    for j in range(0, cycle_order):
        fit_matrix[:, f_col] = ((time - time[0]) / (time[-1] - time[0]))**j if j > 0 else 1.0
        f_col += 1

    for t1, t2 in zip(cycle_times[:-1], cycle_times[1:]):
        t_scale = _macaulay(time - t1)
        for j in range(cycle_order, knot_order+1):
            if j == 0:
                i_start = np.argmax(t_scale > 0)
                fit_matrix[i_start:, f_col] = 1.0
            else:
                fit_matrix[:, f_col] = t_scale ** j
            f_col += 1

        for t_knot in t_knots:
            t_k = t1 + (t2 - t1) * t_knot
            if knot_order == 0:
                i_start = np.argmax(time > t_knot)
                fit_matrix[i_start:, f_col] = 1.0
            else:
                fit_matrix[:, f_col] = _macaulay(time - t_k) ** knot_order
            f_col += 1

    return fit_matrix


def _macaulay(t):
    """The Macaulay function"""
    t_ret = np.zeros(len(t))
    t_ret[t > 0] = t[t > 0]
    return t_ret


def minimize(objective_function, t0, dt_init, dt_max, dt_change_tol, max_iter=100):
    """ Minimize the error returned by objective_function by changing the cycle time t


    :param objective_function: The objective function should have a signature e, evec = fun(t).
                               Key assumption: Each item in evec, which has the same length as t,
                               is almost independent on other items in t than at the same position.
    :type objective_function: callable

    :param t0: Initial guess for cycle times
    :type t0: np.array

    :param dt_init: Initial change of time
    :type dt_init: float

    :param dt_max: Maximum change of time from t0
    :type dt_max: float

    :dt_change_tol: Optimization end criterion: Quit when all items in t change less than this value
    :dt_change_tol: float

    :param max_iter: Maximum number of iterations before ending
    :type max_iter: int

    :return: The vector t that minimize the objective function
    :rtype: np.array
    """

    dt_mat = np.zeros((4, len(t0)))
    fe_mat = np.zeros((4, len(t0)))
    e, fe_mat[0, :] = objective_function(t0)
    dt_change = dt_init
    err_save = [e]
    for n_iter in range(max_iter):
        _update_mat(dt_mat, fe_mat, dt_change, dt_max, n_iter)
        e_old = e
        e, fe_mat[0, :] = objective_function(t0 + dt_mat[0, :])
        err_save.append(e)
        if e > e_old and n_iter > 0:
            dt_change = dt_change / 2

        if np.all(np.abs(dt_mat[0, :]-dt_mat[1, :]) < dt_change_tol):
            break

    return t0 + dt_mat[0, :]


def _update_mat(dt_mat, fe_mat, dt_change, dt_max, n_iter):
    """ Update dt by quadratic approximation, :math:`E=k_2t^2+k_1t+k_0`.
    If k_2<0, then just move in negative gradient by dt_cur
    If k_2>0 (convex), then :math:`t=-k_1/(2k_2)`

    """
    # Update matrices
    for i in range(dt_mat.shape[0]-1, 0, -1):
        dt_mat[i, :] = dt_mat[i-1, :]
        fe_mat[i, :] = fe_mat[i-1, :]

    if n_iter == 0:  # First iteration, do same change for all
        dt_mat[0, :] += dt_change
        return
    elif n_iter == 1:  # Second iteration, move in negative gradient direction
        dt_mat[0, :] += np.array(
            [1 if fe_new < fe_old else -2 for fe_new, fe_old in zip(fe_mat[1, :], fe_mat[2, :])]) * dt_change
        return

    for i in range(dt_mat.shape[1]):
        a = np.transpose([dt_mat[1:4, i] ** j for j in range(3)])
        b = fe_mat[1:4, i]
        k = np.linalg.lstsq(a, b, rcond=None)[0]
        dt_mat[0, i] = -k[1] / (2 * k[2])

        if k[2] < 0 or np.abs(dt_mat[0, i]) > dt_max:  # Concave or too large dt
            #  Move in negative gradient direction with length dt_cur
            if ((fe_mat[1, i] - fe_mat[2, i])/(dt_mat[1, i] - dt_mat[2, i])) < 0:  # de/dt < 0
                dt_mat[0, i] = dt_mat[1, i] + dt_change
            else:
                dt_mat[0, i] = dt_mat[2, i] - dt_change


def def_scale_fun(t, t5=0.25):
    """ Function returning a scale. At t=0 it is 1, and it decreases with distance from t=0

    :param t: The time vector for which the function is evaluated
    :type t: ndarray

    :param t5: The absolute value of the time when the function is 5 %
    :type t5: float

    :returns: The scaling function, same length as t
    :rtype: ndarray
    """
    return np.exp(-3*(t/t5)**2)


def get_objfun(data, keys, knots=0, knot_order=1, cycle_order=0, scale_fun=def_scale_fun, max_ind=0):
    """ Return a callable (function) that has interface 
    :code:`e, evec = fun(t)`. 
    That function can be used as input to :py:func:`minimize`

    - ``t`` is a cycle time vector for which the error is evaluated.
    - ``e`` is the error (scalar float)
    - ``evec`` is the error vector corresponding to each time instance

    Parameters ``knots``, ``knot_order``, and ``cycle_order`` are passed 
    to the :py:func:`smooth_data` function. ``scale_fun`` is used to 
    scale the residual vector for each cycle time to connect the error 
    in the viscinity of each time (this makes it possible to make good 
    updates for the time points as we assume that changing one time
    point will only affect the residual nearby that time point)
    ``data`` is the data to be evaluated for ``keys`` (both are passed 
    to smooth_data)

    """
    def objective_function(t):
        sdata = smooth_data(data, t, keys, knots, knot_order, cycle_order, max_ind=max_ind)
        err = 0.0
        evec = np.zeros(len(t))
        for key in keys:
            sfac = 1.0 /(np.max(data[key]) - np.min(data[key]))
            residual = sdata[key] - data[key] if max_ind == 0 else sdata[key] - data[key][:max_ind]
            err += np.linalg.norm(residual) * sfac
            for i in range(len(evec)):
                evec[i] += np.linalg.norm(residual*scale_fun(sdata['time']-t[i])) * sfac
        return err, evec

    return objective_function
