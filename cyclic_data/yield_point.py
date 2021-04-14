import numpy as np
import cyclic_data.von_mises as vm
import cyclic_data.cycle as ct


def get_yield(td, pv_inds, yield_offset=0.001, delta_vm=(30, 200)):
    """ Return information about each segment in pv_inds with elastic constants and yield stress

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
            c = get_compliance(td, [i1_el, i2_el])
            yp = get_yield_point(td, [i1, i2], c, offset=yield_offset, dvm_ep0=delta_vm_min)
            yield_info['Emod'][iseg].append(1.0 / c[2])
            yield_info['Gmod'][iseg].append(1.0 / c[3])
            for key in keys[2:]:
                yield_info[key][iseg].append(yp[key])

        for key in yield_info:
            yield_info[key][iseg] = np.array(yield_info[key][iseg])

        iseg += 1

    return yield_info


def get_compliance(td, inds, anisotropic=False):
    """ Solve C to approximate [eps-e0, gam-g0]^T = C [sig, tau]^T.
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
    """

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


def get_elastic_strain(td, inds, compliance):
    """ Calculate the elastic strains between inds[0] and inds[1] given the compliance"""

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

    :param td:  Test data, dictionary with time series arrays
    :type td: dict

    :param inds: Start and stop indices of the cycle to be considered
    :type inds: list[ int ]

    :param compliance: Compliance matrix, :math:`C`, such that [eps_el, gam_el]^T = C [sig, tau]^T
    :type compliance: np.array

    :param offset: von Mises strain offset used to detect yield limit
    :type offset: float

    :param dvm_ep0: Change in von Mises stress space until point where plastic strain is considered zero
                    This makes it possible to avoid potential inaccuracies at the beginning of the cycle
                    Default value -1.0 ensures that the first datapoint in the cycle is used by default
    :type dvm_ep0: float

    :returns: The yield point as a dictionary with all keys in data interpolated
              to the yield point. I.e. all items are floats
    :rtype: dict

    """
    ia = np.arange(inds[0], inds[1])
    delta_svm = vm.vm(td['sig'][ia]-td['sig'][inds[0]], td['tau'][ia]-td['tau'][inds[0]])
    i_zero_ep = np.argmax(delta_svm > dvm_ep0)
    eps_el, gam_el = get_elastic_strain(td, inds, compliance)
    eps_pl, gam_pl = (td['eps'][ia] - eps_el, td['gam'][ia] - gam_el)

    deps_pl, dgam_pl = (eps_pl - eps_pl[i_zero_ep], gam_pl - gam_pl[i_zero_ep])

    d_ep_vm = vm.evm(deps_pl, dgam_pl)
    i_above = np.argmax(d_ep_vm > offset)     # First index that ep_vm > offset

    # y(x) = y(x0) + (y(x1)-y(x0))*(x-x0)/(x1-x0)
    interp_coeff = (offset - d_ep_vm[i_above-1])/(d_ep_vm[i_above] - d_ep_vm[i_above-1])
    i1 = inds[0] + i_above
    i0 = i1 - 1
    yield_point = {key: td[key][i0] + (td[key][i1]-td[key][i0])*interp_coeff for key in td}

    return yield_point




