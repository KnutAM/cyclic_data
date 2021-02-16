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
