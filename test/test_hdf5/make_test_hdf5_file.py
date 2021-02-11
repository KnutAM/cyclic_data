""" This scripts generates a hdf5 file to be used for testing the Hdf5Data class in load_hdf5_data.py
The script should be run locally in its folder.
"""

import numpy as np
import h5py

# Attributes and data sets for each test bar (group)
default_attr = {'batch_date': '2020-01-01', 'description': 'description',
                'gauge_length': 12.0, 'inner_diameter': 12.0, 'outer_diameter': 14.0, 'concentricity': 0.01,
                'load_angle': 0, 'pdef_level': 3, 'test_date': '2021-01-01',
                'load_type': 'load_type', 'material': 'R260', 'material_state': 'predeformed'}
default_dset_fields = ['acnt', 'astr', 'disp', 'forc', 'rota', 'tcnt', 'time', 'torq', 'tstr']


def add_group(hdf_file, name, attr={}):
    data_length = 10
    grp = hdf_file.create_group(name)
    for key in default_attr:
        grp.attrs.create(key, default_attr[key])
    for key in attr:
        grp.attrs.create(key, attr[key])    # Overwrite default attribute
    for dset_field in default_dset_fields:
        grp.create_dataset(name=dset_field,data=np.zeros(data_length))

    return grp


hdf = h5py.File('test_file.hdf5', 'w')

add_group(hdf, name='T01', attr={'load_angle': 0, 'load_type': 'Proportional', 'pdef_level': 0})
add_group(hdf, name='T02', attr={'load_angle': 0, 'load_type': 'Proportional', 'pdef_level': 1})
add_group(hdf, name='T03', attr={'load_angle': 0, 'load_type': 'non-proportional', 'pdef_level': 1})

hdf.close()

