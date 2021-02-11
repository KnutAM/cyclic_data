import pathlib as pl
import numpy as np
import h5py
from cyclic_data.data_path import data_path as default_data_path

class Hdf5Data:
    def __init__(self, hdf5_data_file=pl.Path(default_data_path) / 'test_data.hdf5'):
        self.hdf = h5py.File(hdf5_data_file, 'r')

    def get_data_by_attributes(self, attributes):
        """ Get groups in the hdf5 data whose attributes match those provided to the function
        :param attributes: Dictionary with attributes to search for
        :type attributes: dict

        :return: list of data and attributes for the found groups. The data format is given by get_data_by_group
        :rtype: list[dict, dict]
        """
        data = []
        attr = []
        for grp_name in self.hdf:
            group = self.hdf[grp_name]
            attr_match = True
            for key in attributes:
                if group.attrs[key] != attributes[key]:
                    attr_match = False

            if attr_match:
                tmp_data, tmp_attr = self.get_data_by_group(grp_name)
                tmp_attr['group'] = grp_name
                data.append(tmp_data)
                attr.append(tmp_attr)

        return data, attr

    def get_data_by_group(self, grp_name):
        """ Get the test data by group name
        :param grp_name: The name of the group to get data for
        :type grp_name: str

        :return: A dictionary with data with the following keys:
                 time, sig (normal stress), eps (normal strain),
                 tau (shear stress), gam (shear strain),
                 stp (step/cycle in the experiment)
        :rtype: dict
        """

        if grp_name not in list(self.hdf.keys()):
            print(grp_name + 'is not in hdf file')
            return None, None

        ri = self.hdf[grp_name].attrs['inner_diameter']/2.0
        ro = self.hdf[grp_name].attrs['outer_diameter']/2.0
        gl = self.hdf[grp_name].attrs['gauge_length']

        area = np.pi*(ro**2 - ri**2)
        rm = (ri + ro)/2.0

        data = {'time': np.array(self.hdf[grp_name]['time']),
                'sig': np.array(self.hdf[grp_name]['forc'])/area,
                'eps': np.array(self.hdf[grp_name]['astr']),
                'tau': np.array(self.hdf[grp_name]['torq'])/(area*rm),
                'gam': np.array(self.hdf[grp_name]['tstr'])*rm/gl,
                'stp': np.array(self.hdf[grp_name]['acnt']) + np.array(self.hdf[grp_name]['tcnt'])}

        return data, dict(self.hdf[grp_name].attrs)
