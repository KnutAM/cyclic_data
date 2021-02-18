import numpy as np
import h5py


class Hdf5Data:
    """ This class is used to get test data from an hdf5 data file containing data from biaxial
    testing of thin-walled test bars. The data should be organized with one group per test bar.
    This group should contain information about the test bar in the group attributes, at least:

    - ``inner_diameter``: [mm]
    - ``outer_diameter``: [mm]
    - ``gauge_length``: [mm]

    The groups must contain the following datasets

    - ``time``: Experiment time [s]
    - ``forc``: Axial force [N]
    - ``astr``: Axial strain [-]
    - ``acnt``: Axial cycle count
    - ``torq``: Torque [Nmm]
    - ``tstr``: Torsional rotation over ``gauge_length`` [rad]
    - ``tcnt``: Torsional cycle count

    :param hdf5_data_file: The path to the hdf5 data file
    :type hdf5_data_file: str
    """

    def __init__(self, hdf5_data_file):
        """ Constructor method
        """
        self.hdf = h5py.File(hdf5_data_file, 'r')

    def get_data_by_attributes(self, attributes):
        """ Get groups in the hdf5 data whose attributes match those provided to the function

        :param attributes: Dictionary with attributes to search for
        :type attributes: dict

        :raises KeyError: If a key in ``attributes`` is not present in all groups at the top level in the hdf5 file

        :return: lists of data and attributes for the found groups. The data format is given by
                 :py:func:`get_data_by_group`
        :rtype: list[ dict ], list[ dict ]
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
        """ Get the test data by group name.
        The test bar has inner radius :math:`r_i`, outer radius :math:`r_o`,
        and gauge length :math:`L_g`. The test data contain ``forc``, :math:`F_z`,
        ``torq``, :math:`T_z`, rotation ``tstr``, :math:`\\phi_z`, and the axial strain
        ``astr``, :math:`\\epsilon_{zz}`. The following mean values are then given:

        .. math::

            \\sigma_{zz} &= \\frac{F_z}{\\pi (r_o^2-r_i^2)}

            \\sigma_{\\theta z} &= \\frac{T_z}{\\pi r_m(r_o^2-r_i^2)}, \\quad r_m = \\frac{r_i+r_o}{2}

            2\\epsilon_{\\theta z} &= \\phi_z \\frac{r_m}{L_g}

        :param grp_name: The name of the group to get data for
        :type grp_name: str

        :return: A dictionary with numpy array entries with the following keys:

                 - ``time``: Experiment time [s]
                 - ``stp``: Cycle count (``acnt`` + ``tcnt``)
                 - ``sig``: axial stress, :math:`\\sigma_{zz}` [MPa]
                 - ``eps``: axial strain, :math:`\\epsilon_{zz}` [-]
                 - ``tau``: shear stress, :math:`\\sigma_{\\theta z}` [MPa]
                 - ``gam``: shear strain, :math:`2\\epsilon_{\\theta z}` [-]

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
        
    def is_open(self):
        return True if self.hdf else False
        
    def close(self):
        """ Close the file object
        """
        self.hdf.close()
        
