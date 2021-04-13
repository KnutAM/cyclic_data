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
    for key in ['sig', 'tau']:
        td[key][:i0] = 0
        td[key][i1:] = 0

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
    stiff = np.array([[emod, eg], [eg, gmod]])
    td['sig'] = stiff[0, :] @ np.array([td['eps'], td['gam']])
    td['tau'] = stiff[1, :] @ np.array([td['eps'], td['gam']])
    compliance = np.linalg.inv(stiff)
    c = yp.get_compliance(td, [i0, i1], anisotropic=True)
    assert c[0:2] == approx(0.0)
    assert c[2] == approx(compliance[0, 0])
    assert c[3] == approx(compliance[1, 1])
    assert c[4] == approx(compliance[0, 1])





if __name__ == '__main__':
    test_compliance()
