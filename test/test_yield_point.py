import numpy as np
from pytest import approx

import matplotlib.pyplot as plt

import cyclic_data.von_mises as vm
import cyclic_data.yield_point as yp


def test_compliance():
    num_points = 200
    i0 = int(num_points/10)
    i1 = int(num_points/2)
    td = get_test_strain(num_points, eps_max=0.005, gam_max=0.002, gam_rel_pert=0.1)

    emod, gmod = (210.e3, 80.e3)
    eps0, gam0 = (0.001, 0.0004)

    td['sig'] = emod*(td['eps'] - eps0)
    td['tau'] = gmod*(td['gam'] - gam0)

    # Make sure error would rise if items outside the given inds are used in the fit
    alter_stress(td, [i0, i1])

    # Isotropic data and analysis
    c = yp.get_compliance(td, [i0, i1], anisotropic=False)
    assert len(c) == 4
    assert c[0:2] == approx(np.array([eps0, gam0]))
    assert c[2] == approx(1/emod)
    assert c[3] == approx(1/gmod)

    # Isotropic data but anisotropic analysis
    c = yp.get_compliance(td, [i0, i1], anisotropic=True)
    assert len(c) == 5
    assert c[0:2] == approx(np.array([eps0, gam0]))
    assert c[2] == approx(1 / emod)
    assert c[3] == approx(1 / gmod)
    assert c[4] == approx(0.0)

    # Anisotropic data and analysis
    eg = gmod / 10.0
    td['sig'], td['tau'], compliance = get_anisotropic_stress([emod, gmod, eg], td['eps'], td['gam'])

    c = yp.get_compliance(td, [i0, i1], anisotropic=True)
    assert c[0:2] == approx(0.0)
    assert c[2] == approx(compliance[0, 0])
    assert c[3] == approx(compliance[1, 1])
    assert c[4] == approx(compliance[0, 1])


def test_elastic_strain():
    num_points = 200
    inds = [int(num_points/10), int(num_points/2)]
    td = get_test_strain(num_points, eps_max=0.005, gam_max=0.002)

    emod, gmod, eg = (210.e3, 80.e3, 10.e3)
    eps0, gam0 = (0.001, 0.0004)

    # Isotropic data
    td['sig'] = emod*(td['eps'] - eps0)
    td['tau'] = gmod*(td['gam'] - gam0)
    # Change data outside inds to check that this data is not used
    alter_stress(td, inds)

    compliance = np.array([eps0, gam0, 1.0/emod, 1.0/gmod])
    eps_el, gam_el = yp.get_elastic_strain(td, inds, compliance)

    assert eps_el == approx(td['eps'][inds[0]:inds[1]] - eps0)
    assert gam_el == approx(td['gam'][inds[0]:inds[1]] - gam0)

    # Anisotropic data
    td['sig'], td['tau'], comp_mat = get_anisotropic_stress([emod, gmod, eg], td['eps'], td['gam'])
    compliance = np.array([0.0, 0.0, comp_mat[0, 0], comp_mat[1, 1], comp_mat[0, 1]])
    eps_el, gam_el = yp.get_elastic_strain(td, inds, compliance)
    assert eps_el == approx(td['eps'][inds[0]:inds[1]])
    assert gam_el == approx(td['gam'][inds[0]:inds[1]])


def test_yield_point():
    # Test the yield point by defining first the plastic strains and the total strains.
    # Then use np.interp to find the yield point.
    num_points = 200
    evm_lim = 0.0001
    inds = [0, num_points]
    td = get_test_strain(num_points, eps_max=0.005, gam_max=0.002)
    emod, gmod = (70.e3, 70.e3/3.0)
    strains_pl = []
    for pl_max in [0.001, 0.0004]:
        strain_pl = np.zeros(num_points)
        ind_y = np.argmax(td['time']>0.5)
        strain_pl[ind_y:] = pl_max*((td['time'][ind_y:]-td['time'][ind_y])/(td['time'][-1]-td['time'][ind_y]))**2
        strains_pl.append(strain_pl)

    eps_pl = strains_pl[0]
    gam_pl = strains_pl[1]
    evm_pl = vm.evm(eps_pl, gam_pl)

    eps_el = td['eps'] - eps_pl
    gam_el = td['gam'] - gam_pl
    td['sig'] = emod * eps_el
    td['tau'] = gmod * gam_el

    yp_check = {key: np.interp(evm_lim, evm_pl[ind_y:], td[key][ind_y:]) for key in td}
    yield_point = yp.get_yield_point(td, inds, [0.0, 0.0, 1/emod, 1/gmod], offset=evm_lim)

    for key in td:
        assert yp_check[key] == approx(yield_point[key]), 'yield_point[' + key + '] was incorrect'


# Utility functions
def get_test_strain(num_points, eps_max, gam_max, t_max=1.0, gam_rel_pert=0.0):
    """ Create test data with linear time, eps, and gam fields
    Note: gam_field random perturbed to not have all channels fully proportional"""
    td = {'time': np.linspace(0, t_max, num_points)}
    # Define strains. Note random to inflict non-proportionality
    # (otherwise, anisotropic identification is ill-conditioned)
    td['eps'] = (eps_max/t_max)*td['time']
    td['gam'] = (gam_max/t_max) * td['time'] * (1 + gam_rel_pert * (2 * np.random.rand(num_points) - 1))

    return td


def get_anisotropic_stress(stiff_param, eps, gam):
    emod, gmod, eg = stiff_param
    stiff = np.array([[emod, eg], [eg, gmod]])
    sig = stiff[0, :] @ np.array([eps, gam])
    tau = stiff[1, :] @ np.array([eps, gam])
    compliance = np.linalg.inv(stiff)
    return sig, tau, compliance


def alter_stress(td, inds):
    n0 = inds[0]
    n1 = len(td['sig']) - inds[1]
    for key in ['sig', 'tau']:
        td[key][:inds[0]] = np.max(td[key])*np.random.rand(n0)
        td[key][inds[1]:] = np.max(td[key])*np.random.rand(n1)


if __name__ == '__main__':
    test_yield_point()
