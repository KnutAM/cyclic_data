import pathlib as pl
import numpy as np
from cyclic_data.load import Hdf5Data

hdf5_test_file = pl.Path(__file__).parent / 'test_file.hdf5'


def test_test_file():
    """ Verify that the Hdf5Data class can initialize correctly by opening the test file
        This test isolates that the test file used to verify other functionalities is working
    """
    try:
        hdf5 = Hdf5Data(hdf5_test_file)
    except Exception as e:
        assert False, "opening test file raised " + str(e)
    
    assert isinstance(hdf5, Hdf5Data)   # Ensure that instance exists
    assert hdf5.is_open()               # Ensure that file is open
    
    hdf5.close()
    assert not hdf5.is_open()           # Ensure that file is closed


def test_get_data_by_group():
    existing_group = 'T01'
    hdf5 = Hdf5Data(hdf5_test_file)
    data, attr = hdf5.get_data_by_group(existing_group)
    assert isinstance(data, dict)
    assert 'time' in data
    assert isinstance(data['time'], np.ndarray)
    assert isinstance(attr, dict)
    assert 'load_angle' in attr
    assert 'group' not in attr, '"group" should not be in attributes when returned from get_by_group'

    non_existing_group = 'non_existing'
    data, attr = hdf5.get_data_by_group(non_existing_group)
    assert data is None
    assert attr is None


def test_get_data_by_attributes():
    hdf5 = Hdf5Data(hdf5_test_file)

    # Test that function fails for an attribute not in the data
    def verify_failure():
        attr = {'load_angle': 0, 'non_existing_attr': ''}
        try:
            hdf5.get_data_by_attributes(attr)
            print('Should exit with error if a non-existing attribute is requested')
            return False
        except KeyError:  # Should fail with KeyError if attribute not found in file
            return True
        except Exception as e:
            print('Should give KeyError for non-existing attribute, but the following was thrown:')
            print(e.__class__)
            print(e)
            return False

    assert verify_failure()

    # Test that a list is returned
    # Test that the list has length 2 if 2 attributes match
    attr = {'load_angle': 0, 'load_type': 'Proportional'}
    data, attr = hdf5.get_data_by_attributes(attr)
    assert isinstance(data, list)
    assert isinstance(attr, list)
    assert len(data) == len(attr)
    assert len(data) == 2

    # Test that the list is empty if no attributes match
    attr = {'load_angle': 0, 'load_type': 'does_not_exist'}
    data, attr = hdf5.get_data_by_attributes(attr)
    assert len(data) == 0
    assert len(attr) == 0
