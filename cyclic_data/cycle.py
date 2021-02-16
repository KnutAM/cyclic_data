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
