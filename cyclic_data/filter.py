import copy
import numpy as np


def smoothen(test_data, pv_inds, filter_functions, keys=None):
    """Smoothens the test_data within each pv_inds with given filter_functions.
    If filter_function is a dict with filter functions, test_data with those keys are smoothened.
    If filter_function is just a single function, all test_data quantities (except 'time' and 'stp') are filtered
    Unless keys are given, in which case only those quantities are filtered.
    The returned data is a direct replacement for test_data, with each quantity having the same time points as the
    original data

    :param test_data: dict with numpy arrays of equal lengths, required to contain a 'time' key
    :type test_data: dict

    :param pv_inds: list of lists of indices describing interesting points between which the the filter will be applied
    :type pv_inds: list[ iterable ]

    :param filter_functions: Either a dictionary of filter functions or a single filter function
                             Function should be interface vf = filter_function(t, v) where
                             t is time, v are values at corresponding time and vf are corresponding smoothened values
    :type filter_functions: dict or function

    :param keys: List of keys in test_data to apply filter to. If None (default), apply to keys in filter_functions,
                 or to all (except 'time' and 'stp') if filter_functions is a single function
    :type keys: list[ str ]

    :returns: smoothened test data including test data that was not smoothened in original form
    :rtype: dict
    """

    # Create output data structure
    test_data_smooth = copy.deepcopy(test_data)

    # Decide which quantities to smoothen
    if keys is None:
        if isinstance(filter_functions, dict):
            keys = [key for key in filter_functions]
        else:
            keys = [key for key in test_data if key not in ['time', 'stp']]

    # If not existing, create function dictionary
    fdict = filter_functions if isinstance(filter_functions, dict) else {key: filter_functions for key in keys}

    # Reshape indices (note, pv_inds should be sorted!)
    inds = np.sort([i for j in pv_inds for i in j])

    # Apply filter
    for i0, i1 in zip(inds[:-1], inds[1:]):
        for key, f in zip(keys, fdict):
            test_data_smooth[key][i0:i1] = f(test_data['time'], test_data[key])

    return test_data_smooth
