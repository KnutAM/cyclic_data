import numpy as np
from pytest import approx

import cyclic_data.yield_point as yp


def test_compliance():
    num_points = 200

    td = {'time': np.linspace(0, 1, num_points)}
    emod, gmod = (210.e3, 80.e3)
    eps0, gam0 = (0.001, 0.0004)

    # Define strains. Note random to inflict non-proportionality
    # (otherwise, anisotropic identification is ill-conditioned)

    td['eps'] = 0.005*td['time']
    td['gam'] = 0.01 * td['time'] * (1 + 0.01 * (2 * np.random.rand(num_points) - 1))
    td['sig'] = emod*(td['eps'] - eps0)
    td['tau'] = gmod*(td['gam'] - gam0)

    i0 = int(num_points/10)
    i1 = int(num_points/2)

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

    td = {'time': np.linspace(0, 1, num_points)}
    emod, gmod, eg = (210.e3, 80.e3, 10.e3)
    eps0, gam0 = (0.001, 0.0004)

    td['eps'] = 0.005*td['time']
    td['gam'] = 0.01 * td['time']

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
    test_compliance()
    test_elastic_strain()
