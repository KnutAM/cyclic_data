import numpy as np
import h5py
import os
import shutil
import cyclic_data.utils.html as html


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

    def make_html_table(self, attrs, formats=None, 
                        output_dir='test_data_html_table'):
        """ Generate an html table with the attributes to 
        give an overview over the available test data. 
        
        :param attrs: List of attributes to output
        :type attrs: Iterable[ str ]
        
        :param formats: List of format codes for each column without 
                        percent sign. If not given, default str() 
                        conversion is used. Example codes are
                        
                        - 's': string
                        - '5.2f': float with length 5 and 2 decimal pts
                        - '10.4e': exponential with length 5 and 4 pts
                        
        :type formats: Iterable[ str ]
        
        :param output_dir: The directory in which to save 
                           the html output
        :type output_dir: str
        
        """
        # Fix internal formats
        if formats is None:
            _formats = None
        else:
            assert len(formats) == len(attrs), ('list of formats must '
                                                + 'be equally long as '
                                                + 'list of attributes '
                                                + 'to add to table')
            _formats = formats[:]
            _formats.insert(0, 's') # Insert string for group name
        
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        os.mkdir(output_dir)
        html_path = os.path.join(output_dir, 'test_data.html')
        with open(html_path, 'w') as html_fid:
            # Include the fixed content before the table
            html_fid.write(html.get_pre_table())
            
            # Generate the table contents from the hdf attributes
            # Extract table header
            header = ['test bar']
            for key in attrs:
                header.append(key)
            # Extract table content 
            content = []
            for grp_name in self.hdf:
                grp = self.hdf[grp_name]
                content.append([grp_name])
                for key in attrs:
                    content[-1].append(grp.attrs[key])
            html_fid.write(html.table(head=header, body=content, 
                                      foot=header, body_formats=_formats))
                
            # Include the fixed content after the table
            html_fid.write(html.get_post_table())
        
        # Create fixed style and script files in created folder
        with open(os.path.join(output_dir, 'style.css'), 'w') as fid:
            fid.write(html.get_table_style())
        with open(os.path.join(output_dir, 'table.js'), 'w') as fid:
            fid.write(html.get_table_script())
        
    def is_open(self):
        return True if self.hdf else False
        
    def close(self):
        """ Close the file object
        """
        self.hdf.close()
        
