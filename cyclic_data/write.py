""" Write data based on raw experimental test files
"""

import h5py
import numpy as np

_required_cols = ['time', 'forc', 'astr', 'acnt', 'torq', 'tstr', 'tcnt']
_required_attr = ['inner_diameter', 'outer_diameter', 'gauge_length']
_default_descr = {'time': 'Experiment time [s]',
                  'forc': 'Axial force [N]',
                  'astr': 'Axial strain [-]',
                  'acnt': 'Axial cycle count',
                  'torq': 'Torque [Nmm]',
                  'tstr': 'Torsional rotation over the gauge length [rad]',
                  'tcnt': 'Torsional cycle count',
                  'disp': 'Axial displacement for entire test bar [mm]',
                  'rota': 'Rotation of entire test bar [rad]'}


class Hdf5Write:
    """ This class is used to write test data from biaxial testing of thin-walled test bars,
    reported in raw text files to an hdf5 data file. Example usage:

    .. code-block:: python

        import numpy as np
        from cyclic_data.write import Hdf5Write

        # Common for all test bars
        cols_dict = {'time': 0, 'acnt': 1, 'forc': 2, 'astr': 3, 'disp': 4,
                     'tcnt': 5, 'torq': 6, 'tstr': 7, 'rota': 8}
        cols_dtype = {'acnt': np.uint32, 'tcnt': np.uint32}
        hdf = Hdf5Write('test_data.hdf5',cols_dict,cols_dtype=cols_dtype)

        # For each test bar
        test_bar = 'T01'
        attrs = {'inner_diameter': 12.0, 'outer_diameter': 14.0, 'gauge_length': 12.0, 'test_type': 'ratcheting'}
        data = np.loadtxt('T01.txt')    # Read in data from text file, with columns according to cols_dict
        hdf.add_bar(data, test_bar, attrs)

        # Close the hdf object in the end
        hdf.close()

    :param name: The path to the hdf5 data file
    :type name: str

    :param cols_dict: The column number (starting with 0) in the text file pertaining to the key.
                      Note that the following keys are standardized and must be used. If not available, this is ok
                      but the data will be assumed to be zero

                      - ``time``: Experiment time [s]
                      - ``forc``: Axial force [N]
                      - ``astr``: Axial strain [-]
                      - ``acnt``: Axial cycle count
                      - ``torq``: Torque [Nmm]
                      - ``tstr``: Torsional rotation over ``gauge_length`` [rad]
                      - ``tcnt``: Torsional cycle count

                      By convension, the following keys are recommended to use if available, but this is not required

                      - ``disp``: Axial displacement for entire test bar [mm]
                      - ``rota``: Rotation of entire test bar [rad]

    :type cols_dict: dict

    :param cols_descr: Description of each column. If not added default descriptions will be added, see description
                       of ``cols_dict`` (and also ``_default_descr`` in source code)
    :type cols_descr: dict

    :param cols_dtype: Description of the datatype to save each column as. Defaults to np.float64 for all, but to reduce
                       file size, some columns could be saved as e.g. np.float32 or even np.intXX.
    :type cols_dtype: dict

    """

    def __init__(self, name, cols_dict, cols_descr=None, cols_dtype=None):
        """ Initialize of Hdf5Write
        """
        self.hdf5 = h5py.File(name, 'w')

        # Add default values as -1 for required columns (i.e. all values to zero)
        self.cols = {key: -1 for key in _required_cols}

        # Add given values
        for key in cols_dict:
            self.cols[key] = cols_dict[key]

        # Add column description (first default, then add/overwrite if given)
        self.cols_descr = {key: _default_descr[key] for key in _default_descr}
        if cols_descr is not None:
            for key in cols_descr:
                self.cols_descr[key] = cols_descr[key]

        # Add default data type and then add/overwrite given dtypes.
        self.cols_dtype = {key: np.float64 for key in self.cols}
        if cols_dtype is not None:
            for key in cols_dtype:
                self.cols_dtype[key] = cols_dtype[key]

    def add_bar(self, data_matrix, name, attrs):
        """ Add a test bar to the datafile.

        :param data_matrix: A matrix containing the test data, such that all data from column c is accessed as
                            data_matrix[:,c]
        :type data_matrix: np.array

        :param name: Name of the test bar to add, this will be the name of the hdf5 group
        :type name: str

        :param attrs: Dictionary of attributes to add for the test bar. Must at least contain the
                      following keys: ``inner_diameter``, ``outer_diameter``, and ``gauge_length``.
        :type attrs: dict

        """
        # Check that required attributes are supplied
        if not all([r in attrs for r in _required_attr]):
            print('The following required attributes are missing')
            print([r for r in _required_attr if r not in attrs])
            raise ValueError

        # Add group with attributes
        grp = self.hdf5.create_group(name)
        for key in attrs:
            grp.attrs[key] = attrs[key]

        # Add datasets to the group
        for key in self.cols:
            col = self.cols[key]
            data = data_matrix[:, col] if col >= 0 else np.zeros(data_matrix.shape[0])
            ds = grp.create_dataset(key, shape=(data_matrix.shape[0],), dtype=self.cols_dtype[key], data=data)
            ds.attrs['description'] = self.cols_descr[key] if key in self.cols_descr else key

    def close(self):
        """ Close the hdf5 file object when done"""
        self.hdf5.close()
