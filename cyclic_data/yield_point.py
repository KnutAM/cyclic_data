""" `yield_point.py` is used to determine the yielding characteristics of the cyclic data
"""
import numpy as np
import cyclic_data.von_mises as vm
import cyclic_data.cycle as ct


def get_yield(td, pv_inds, yield_offset=0.001, delta_vm=(-1, 200), axial=True, shear=True):
    """ Return yield-related information about each segment in pv_inds.
    Specifically, the elastic constants and the yield point (eps, sig,
    gam, tau, time at yielding). A segment denotes the data between e.g. a valley the next peak.

    :param td: Test data for which the yield points should be calculated. The keys 'sig',
               'eps', 'tau', 'gam', and 'time' are required. Content should be np.ndarray
    :type td: dict

    :param pv_inds: Indices of peaks and valleys (note that more than 2 per cycle is possible,
                    see :py:func:`ct.get_pv_inds`_
    :type pv_inds: list[ np.ndarray ]

    :param yield_offset: The amount of effective von mises plastic strain change used to define yielding
    :type yield_offset: float

    :param delta_vm: Values of change in von mises stress between which the compliance is calculated.
                     The first (lower) value determines the plastic strain increment zero point, and
                     it is not possible to identify a yield limit below this value. In general, if a yield
                     value is determined within the range of delta_vm, the range is a bad choice as the material
                     should behave elastically in this range.
    :type delta_vm: iterable

    :param axial: Should the axial compliance/stiffness be obtained? If false, compliance is set to zero
    :type axial: bool

    :param shear: Should the shear compliance be obtained? If false, compliance is set to zero
    :type shear: bool

    :returns: A dictionary containing the elastic parameters ('Emod', 'Gmod'), as well as the following data
              at the time of yielding: 'eps', 'sig', 'gam', 'tau', 'time'. Each item is a list of different
              types of segments (e.g. first item is valley to peak and second is peak to valley). The items
              in this list are np.ndarrays describing that yield point for all cycles
    :rtype: dict

    """

    delta_vm_min = delta_vm[0]  # Minimum stress change to use when calibrating elastic parameters
    delta_vm_max = delta_vm[1]  # Maximum stress change to use when calibrating elastic parameters.
    keys = ['Emod', 'Gmod', 'eps', 'sig', 'gam', 'tau', 'time']
    yield_info = {key: [[] for _ in pv_inds] for key in keys}
    inds1, inds2 = ct.get_segments(pv_inds)
    iseg = 0
    for ind1, ind2 in zip(inds1, inds2):
        for i1, i2 in zip(ind1, ind2):
            delta_vm = vm.vm(td['sig'][i1:i2]-td['sig'][i1], td['tau'][i1:i2]-td['tau'][i1])
            i1_el = np.argmax(delta_vm > delta_vm_min) + i1
            i2_el = np.argmax(delta_vm > delta_vm_max) + i1
            c = get_compliance(td, [i1_el, i2_el], axial=axial, shear=shear)
            yp = get_yield_point(td, [i1, i2], c, offset=yield_offset, dvm_ep0=delta_vm_min)
            if axial:
                yield_info['Emod'][iseg].append(1.0 / c[2])
            if shear:
                yield_info['Gmod'][iseg].append(1.0 / c[3])
            for key in keys[2:]:
                yield_info[key][iseg].append(yp[key])

        for key in yield_info:
            yield_info[key][iseg] = np.array(yield_info[key][iseg])

        iseg += 1

    return yield_info


def get_compliance(td, inds, anisotropic=False, axial=True, shear=True):
    """ Solve e0, g0, C to approximate [eps-e0, gam-g0]^T = C [sig, tau]^T.
    Formulate problem as, determine c to minimize the least square error of
             a              *    c    =   b
    | 1,  0, sig,   0, tau|             |eps|
    | 0,  1,   0, tau, sig|   | e0 |    |gam|
    | 1,  0, sig,   0, tau|   | g0 |    |eps|
    | 0,  1,   0, tau, sig| * | Cs |  = |gam|
    | 1,  0, sig,   0, tau|   | Ct |    |eps|
    | 0,  1,   0, tau, sig|   | Cst|    |gam|
    | 1,  0, sig,   0, tau|             |eps|
    |       ...           |             |...|
    Last column in a and row in c only applicable if anisotropic is True

    :param td: Test data for which the compliance should be calculated. The keys
               'sig', 'eps', 'tau', and 'gam' are required. Content should be np.ndarray
    :type td: dict

    :param inds: Indices between which test data arrays should be used to calculate
                 the compliance.
    :type inds: list[ int ]

    :param anisotropic: Should anisotropic elasticity be assumed (True) or just
                        isotropic (False)
    :type anisotropic: bool

    :param axial: Should the axial compliance be obtained? If false, it is set to zero
    :type axial: bool

    :param shear: Should the shear compliance be obtained? If false, it is set to zero
    :type shear: bool

    :returns: The compliance vector [e0, g0, Cs, Ct, Cst] (Cst only if anisotropic)
    :rtype: np.ndarray
    """
    # Check input validity
    if anisotropic and not (axial and shear):
        raise ValueError("Cannot have anisotropic if not both axial and shear components are present")
    if not (axial or shear):
        raise ValueError("At least one of axial and shear must be true")

    if axial and shear:

        num_param = 5 if anisotropic else 4
        num_pts = 2*(inds[1]-inds[0])
        # Assemble the stress matrix
        a = np.zeros((num_pts, num_param))
        a[0::2, 0] = 1.0
        a[1::2, 1] = 1.0
        a[0::2, 2] = td['sig'][inds[0]:inds[1]]
        a[1::2, 3] = td['tau'][inds[0]:inds[1]]

        if anisotropic:
            a[0::2, 4] = td['tau'][inds[0]:inds[1]]
            a[1::2, 4] = td['sig'][inds[0]:inds[1]]

        # Assemble the strain matrix
        b = np.zeros(num_pts)
        b[0::2] = td['eps'][inds[0]:inds[1]]
        b[1::2] = td['gam'][inds[0]:inds[1]]

        # Solve for the compliance (including strain offsets e0 and g0)
        c = np.linalg.lstsq(a, b, rcond=None)

        rank = c[2]
        if anisotropic and rank == 4:
            print('Warning: Insufficient rank for anisotropic elastic parameter identification.\n'
                  + '         This can occur if all 4 axial and shear stresses and strains are \n'
                  + '         proportional and the response is isotropic')
        elif rank < 4:
            print('Warning: Insufficient rank for elastic parameter identification.\n'
                  + '         This can occur if e.g. both the shear stress and strain are zero')

        return c[0]

    elif axial:
        p = np.polyfit(td['sig'][inds[0]:inds[1]], td['eps'][inds[0]:inds[1]], deg=1)
        return [p[1], np.mean(td['gam'][inds[0]:inds[1]]), p[0], 0.0]
    elif shear:
        p = np.polyfit(td['tau'][inds[0]:inds[1]], td['gam'][inds[0]:inds[1]], deg=1)
        return [np.mean(td['eps'][inds[0]:inds[1]]), p[1], 0.0, p[0]]


def get_elastic_strain(td, inds, compliance):
    """ Calculate the elastic strains between inds[0] and inds[1]
    given the compliance

    :param td: Test data for which the elastic strains should be calculated. The keys
               'sig' and 'tau' are required. Content should be np.ndarray
    :type td: dict

    :param inds: Indices for the arrays in td between which the elastic strain is calculated
    :type inds: list[ int ]

    :param compliance: Compliance vector, see output from :py:func:`get_compliance`_
    :type compliance: np.ndarray, list

    :returns: The axial and shear elastic strains for the data from inds[0] to inds[1]
    :rtype: np.ndarray, np.ndarray

    """

    if not isinstance(compliance, np.ndarray):
        compliance = np.array(compliance)

    # Determine if the compliance is anisotropic or not
    anisotropic = len(compliance) == 5
    num_cols = 2 if anisotropic else 1
    ia = np.arange(inds[0], inds[1])

    a = np.zeros((len(ia), num_cols))

    # Calculate elastic axial strain
    a[:, 0] = td['sig'][ia]
    if anisotropic:
        a[:, 1] = td['tau'][ia]
    eps_el = a @ compliance[[2, 4]] if anisotropic else a @ compliance[[2]]

    # Calculate elastic shear strain
    a[:, 0] = td['tau'][ia]
    if anisotropic:
        a[:, 1] = td['sig'][ia]
    gam_el = a @ compliance[[3, 4]] if anisotropic else a @ compliance[[3]]

    return eps_el, gam_el


def get_yield_point(td, inds, compliance, offset=0.001, dvm_ep0=-1.0):
    """ Consider the given test data, td, from index inds[0] to index inds[1],
    and determine the yield point (time_y, eps_y, sig_y, gam_y, tau_y)

    :param td:  Test data for which the yield point should be calculated. The keys
               'sig', 'eps', 'tau', and 'gam' are required. Content should be np.ndarray
    :type td: dict

    :param inds: Start and stop indices of the cycle to be considered
    :type inds: list[ int ]

    :param compliance: Compliance vector, see output from :py:func:`get_compliance`_
    :type compliance: np.ndarray, list

    :param offset: von Mises strain offset used to detect yield limit
    :type offset: float

    :param dvm_ep0: Change in von Mises stress space until point where plastic strain is considered zero
                    This makes it possible to avoid potential inaccuracies at the beginning of the cycle
                    Default value -1.0 ensures that the first datapoint in the cycle is used by default
    :type dvm_ep0: float

    :returns: The yield point as a dictionary with all keys in td interpolated to the yield point.
              I.e. all items are floats
    :rtype: dict

    """
    ia = np.arange(inds[0], inds[1])
    delta_svm = vm.vm(td['sig'][ia]-td['sig'][inds[0]], td['tau'][ia]-td['tau'][inds[0]])
    i_zero_ep = np.argmax(delta_svm > dvm_ep0)
    eps_el, gam_el = get_elastic_strain(td, inds, compliance)
    eps_pl, gam_pl = (td['eps'][ia] - eps_el, td['gam'][ia] - gam_el)

    deps_pl, dgam_pl = (eps_pl - eps_pl[i_zero_ep], gam_pl - gam_pl[i_zero_ep])

    d_ep_vm = vm.evm(deps_pl, dgam_pl)
    i_above = np.argmax(d_ep_vm[i_zero_ep:] > offset) + i_zero_ep     # First index that ep_vm > offset

    # y(x) = y(x0) + (y(x1)-y(x0))*(x-x0)/(x1-x0)
    interp_coeff = (offset - d_ep_vm[i_above-1])/(d_ep_vm[i_above] - d_ep_vm[i_above-1])
    i1 = inds[0] + i_above
    i0 = i1 - 1
    yield_point = {key: td[key][i0] + (td[key][i1]-td[key][i0])*interp_coeff for key in td}

    return yield_point




