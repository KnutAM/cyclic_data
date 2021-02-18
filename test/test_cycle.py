import numpy as np
from pytest import approx

import cyclic_data.cycle as cy


def test_get_pv_inds():
    cycles = np.array([0.0, 1.0, 1.0, 1.0, 2.0, 2.0,
                       2.1, 2.1, 2.1, 2.3, 10, 12, 12, 14])
    test_data = {'stp': cycles}

    ind10 = cy.get_pv_inds(test_data, num_per_cycle=1, num_ind_skip=0)
    ind20 = cy.get_pv_inds(test_data, num_ind_skip=0)
    ind31 = cy.get_pv_inds(test_data, num_per_cycle=3, num_ind_skip=1)
    res = [ind10, ind20, ind31]

    ind10_comp = [np.array([1, 4, 6, 9, 10, 11, 13])]
    ind20_comp = [ind10_comp[0][::2], ind10_comp[0][1::2]]
    ind31_comp = [ind10_comp[0][1::3], ind10_comp[0][2::3], ind10_comp[0][3::3]]
    comps = [ind10_comp, ind20_comp, ind31_comp]
    specs = ['ind10', 'ind20', 'ind31']
    test_names = [[spec + ':' + str(nr) for nr, _ in enumerate(comps[i])] for i, spec in enumerate(specs)]
    for rs, cs, tns in zip(res, comps, test_names):
        for r, c, tn in zip(rs, cs, tns):
            assert r == approx(c), 'test ' + tn + ' failed'


def test_get_mid_values():
    # Test for correct identification of mid values
    test_data = {'x': np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])}
    pv_inds = [[1, 4, 9], [2, 7]]
    mid_values = cy.get_mid_values(test_data, qty=['x'], pv_inds=pv_inds)

    assert mid_values['x'][0] == approx([2.5, 6.5])
    assert mid_values['x'][1] == approx([4.0, 9.0])


def test_get_diff_values():
    test_data = {'x': np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
                 'y': np.array([0, 2, 4, 8, 1, 2, 5, 2, 3, 4, 10])}
    pv_inds = [[1, 5, 8], [3, 7, 9]]
    diff_values = cy.get_diff_values(test_data, qty=['y', 'x'], pv_inds=pv_inds)

    assert diff_values['x'][0] == approx([3-1, 7-5, 9-8])
    assert diff_values['x'][1] == approx([5-3, 8-7])
    assert diff_values['y'][0] == approx([8-2, 2-2, 4-3])
