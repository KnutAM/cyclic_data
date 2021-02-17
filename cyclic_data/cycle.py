""" Module used to analyze the cycles within the data
"""
import numpy as np


def get_pv_inds(test_data, num_per_cycle=2, num_ind_skip=0):
    """ Get peak and valley indices (can have more than 2 peaks/valleys per cycle)

    :param test_data: test data as dictionary, must contain 'stp' key with step numbers
    :type test_data: dict

    :param num_per_cycle: Number of peaks/valleys per cycle (i.e. for proportional loading num_per_cycle=2, and for
                          a square loading path num_per_cycle=4
    :type num_per_cycle: int

    :param num_ind_skip: How many step changes to skip in the beginning
    :type num_ind_skip: int

    :return: list of np.arrays with indices for each pv type. list length = num_per_cycle
    :rtype: list[ np.array ]
    """
    def get_increase_indices(arr, tol=1.e-6):
        return np.where(arr[1:]-arr[:-1] > tol)[0] + 1

    ch_ind = get_increase_indices(test_data['stp'])[num_ind_skip:]
    indices = []
    for i in range(num_per_cycle):
        indices.append(ch_ind[i::num_per_cycle])

    return indices


def get_mid_values(test_data, qty, pv_inds):
    """ Get mid values of test_data[qt] for qt in qty. One value for each segment
    as descirbed by pv_inds

    :param test_data: test data as dictionary, must contain fields given by qty
    :type test_data: dict

    :param qty: keys for data in test_data to be calculated mid values for
    :type qty: list[ str ]

    :param pv_inds: A list of list of indices corresponding to certain cycle points.
                    Each outer list contain information about the same point type.
                    E.g. pv_inds[0] gives peak indices, pv_inds[1] gives valley indices.
    :type pv_inds: iterable[ iterable[ int ] ]

    :returns: mid values for each quantity in qty as dictionary. The data are lists with
              length len(pv_inds) containing numpy arrays
    :rtype: dict

    """

    # Find end of segments
    inds2 = [pv[:] for pv in pv_inds[1:]]
    inds2.append(pv_inds[0][1:])

    # Find start of segments (we must ensure that we don't start a segment that
    # has no end index, hence [:len(i2)]
    inds1 = [pv[:len(i2)] for pv, i2 in zip(pv_inds, inds2)]  # Start of segment

    mid_data = {}
    for qt in qty:
        mid_data[qt] = [(test_data[qt][i1] + test_data[qt][i2])/2.0 for i1, i2 in zip(inds1, inds2)]

    return mid_data
